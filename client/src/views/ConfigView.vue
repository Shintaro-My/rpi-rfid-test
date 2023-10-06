<template>
  <div class="wrap">

    <h1>設定</h1>

    <a @click="update()">最新の情報に更新する</a>

    <EasyDataTable
      show-index
      v-model:items-selected="itemsSelected"
      buttons-pagination
      :headers="headers"
      :items="items"
      :loading="loading"
      alternating
    >
      <template #item-operation="item">
        <div class="operation-wrapper">
          <div><a @click="editItem(item)">編集</a></div>
          <div><a @click="deleteItem(item)">削除</a></div>
        </div>
      </template>
      <template #expand="item">
        <div class="memo">
          <div>
            <span class="bold">備考</span>
            {{ item.Note }}
          </div>
        </div>
        
      </template>
    </EasyDataTable>

    <div>
      <a @click="deleteMulti()" v-if="itemsSelected.length">{{ itemsSelected.length }} 件のアイテムを削除</a>
    </div>

    <p>※ 変更は再起動後に反映されます。</p>
    
    <div v-if="edit_visible" class="darkbox">
      <h3>Edit "<pre class="inline">{{ editingItem.Attribute }}</pre>":</h3>
      <div>
        <div>Status:<input type="number" v-model="editingItem.Status" min="0" /></div>
        <div>Note:<input type="text" v-model="editingItem.Note" /></div>
      </div>
      <div class="btns">
        <button @click="_edit()">Save</button>
        <button @click="close_edit()">Cancel</button>
      </div>
    </div>
    
    <div v-if="delete_visible" class="darkbox">
      <h3>Delete "{{ deletingItem.Attribute }}"?</h3>
      <div class="btns">
        <button @click="_delete()">Delete</button>
        <button @click="close_delete()">Cancel</button>
      </div>
    </div>


  </div>
</template>

<script setup lang="ts">
import { defineComponent, ref, reactive } from "vue";
import type { Ref } from "vue";
import type { Header, Item } from "vue3-easy-data-table";
import { saveAs } from 'file-saver';
defineProps<{
  msg: string
}>()
const headers: Header[] = [
  { text: 'Attribute', value: 'Attribute', sortable: true },
  { text: 'Status', value: 'Status' },
  { text: '_', value: 'operation' }
]
const itemsSelected: Ref<Item[]> = ref([]);
const items: Ref<Item[]> = ref([]);

const loading: Ref<boolean> = ref(false);
  
const edit_visible: Ref<boolean> = ref(false);
const delete_visible: Ref<boolean> = ref(false);

const field = ['Attribute', 'Status', 'Note'];


type list = (string | number)[];
const fmt = (ary: list, ...label: string[]) => {
  const obj: { [name: string]: string | number } = {};
  for (let i = 0; i < ary.length; i++) {
    const key = label[i]
    obj[key] = ary[i]
  }
  return obj;
}
const update = async () => {
  loading.value = true;
  const req = await fetch('/config');
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  const json = await req.json()
  const user = json.body;
  items.value = user.map((v: list) => fmt(v, ...field));
  loading.value = false;
  return true;
}


const close_edit = () => {
  edit_visible.value = false;
}
const close_delete = () => {
  delete_visible.value = false;
}

const editingItem = reactive({
  Attribute: '',
  Status: '',
  Note: ''
});
const editItem = (item: Item) => {
  const { Attribute, Status, Note } = item;
  editingItem.Attribute = Attribute;
  editingItem.Status = Status;
  editingItem.Note = Note;
  edit_visible.value = true;
}
const _edit = async () => {
  const { Attribute, Status: _status, Note } = editingItem;
  const Status = Number(_status);
  if (!Attribute) return alert('属性名は空欄にできません')
  if (Status < 0 || isNaN(Status)) return alert('無効な値です')
  loading.value = true;
  const req = await fetch('/config', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ Attribute, Status, Note })
  });
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  close_edit();
  await update();
}

const deletingItem = reactive({
  Attribute: ''
});
const deleteItem = (item: Item) => {
  deletingItem.Attribute = item.UserId;
  delete_visible.value = true;
}
const _delete = async () => {
  loading.value = true;
  const { Attribute } = deletingItem;
  const req = await fetch(`/config?attribute=${Attribute}`, {
    method: 'DELETE'
  });
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  close_delete();
  await update();
}


const deleteMulti = async () => {
  if (!confirm('本当に削除しますか？')) return;
  loading.value = true;
  const attrs = itemsSelected.value.map(v => v.Attribute);
  const req = await fetch(`/config?attribute=${attrs.join(',')}`, {
    method: 'DELETE'
  });
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  close_delete();
  await update();
  itemsSelected.value = [];
}

update();

</script>


<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}
.memo {
  padding: .5em;
}
.bold {
  display: inline-flex;
  justify-content: space-between;
  font-weight: 700;
  width: 5.2em;
}
.bold::after {
  content: ':';
  font-weight: 700;
}
.darkbox {
  background: rgba(43, 43, 43, .9);
  border-radius: 0.35em;
  color: #fff;
  position: fixed;
  top: 25%;
  left: 0;
  right: 0;
  margin: auto;
  max-width: 400px;
  padding: 0.75em 1em;
  z-index: 3;
}
.btns {
  display: flex;
  height: 3em;
  justify-content: space-evenly;
  padding: 1em 0 0;
}
.restore {
  border: 1px dotted;
  border-radius: 0.5em;
  margin: 1.25em 0 0.5em;
  padding: 0.75em;
}
@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
