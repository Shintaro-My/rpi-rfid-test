<template>
  <div class="wrap">

    <h1>登録ユーザー</h1>

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
            <span class="bold">登録日</span>
            {{ item.CreatedAt }}
          </div>
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
    <div>
      <a @click="download()">ログファイルのダウンロード</a>
    </div>
    
    <div v-if="edit_visible" class="darkbox">
      <h3>Edit "<pre class="inline">{{ editingItem.UserId }}</pre>":</h3>
      <div>
        <div>UserName:<input type="text" v-model="editingItem.UserName" /></div>
        <div>Note:<input type="text" v-model="editingItem.Note" /></div>
      </div>
      <div class="btns">
        <button @click="_edit()">Save</button>
        <button @click="close_edit()">Cancel</button>
      </div>
    </div>
    
    <div v-if="delete_visible" class="darkbox">
      <h3>Delete "{{ deletingItem.UserId }}"?</h3>
      <div class="btns">
        <button @click="_delete()">Delete</button>
        <button @click="close_delete()">Cancel</button>
      </div>
    </div>

    
    <div class="restore">
      <h2>ログファイルからの復元</h2>
      <label class="file">
        <input type="file" ref="file" @change="fileChange">
      </label>
      <a @click="restore" v-if="archive && archive.length">ログから復元する</a>
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
  { text: 'UserName', value: 'UserName', sortable: true },
  { text: 'UserId', value: 'UserId', sortable: true },
  { text: 'LastSeen', value: 'LastSeen', sortable: true },
  { text: '_', value: 'operation' }
]
const itemsSelected: Ref<Item[]> = ref([]);
const items: Ref<Item[]> = ref([]);

const loading: Ref<boolean> = ref(false);
  
const edit_visible: Ref<boolean> = ref(false);
const delete_visible: Ref<boolean> = ref(false);

const field = ['UserId', 'UserName', 'Note', 'CreatedAt', 'LastSeen'];


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
  const req = await fetch('/users');
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
const download = async () => {
  await update();
  const blob: Blob = new Blob([JSON.stringify(items.value)], {type: 'application/json'});
  saveAs(blob, 'log.json');
}

const file: Ref<HTMLInputElement | null> = ref(null);
const archive: Ref<object[]> = ref([]);
const fileChange = async() => {
  const files = file.value?.files;
  if (files) {
    const result: object[] | null = await new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.readAsText(files[0]);
      fr.onload = () => {
        try {
          const json: object[] = JSON.parse(fr.result as string);
          resolve(json);
        } catch(e) {
          reject(null);
        }
      }
    })
    if (result && result.length) {
      archive.value = result;
    }
  }
}
const restore = async () => {
  if (confirm('登録ユーザーのリストが上書きされ、未登録IDの履歴が破棄されます。よろしいですか？')) {
    const req = await fetch('/restore', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ Users: archive.value })
    });
    if (req.status != 200) {
      alert('Communication failed.')
      return false;
    }
    await update();
  }
}

const close_edit = () => {
  edit_visible.value = false;
}
const close_delete = () => {
  delete_visible.value = false;
}

const editingItem = reactive({
  UserId: '',
  UserName: '',
  Note: ''
});
const editItem = (item: Item) => {
  const { UserId, UserName, Note } = item;
  editingItem.UserId = UserId;
  editingItem.UserName = UserName;
  editingItem.Note = Note;
  edit_visible.value = true;
}
const _edit = async () => {
  const { UserId, UserName, Note } = editingItem;
  if (!UserName) return alert('ユーザー名は空欄にできません')
  loading.value = true;
  const req = await fetch('/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ UserId, UserName, Note })
  });
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  close_edit();
  await update();
}

const deletingItem = reactive({
  UserId: ''
});
const deleteItem = (item: Item) => {
  deletingItem.UserId = item.UserId;
  delete_visible.value = true;
}
const _delete = async () => {
  loading.value = true;
  const { UserId } = deletingItem;
  const req = await fetch(`/users?id=${UserId}`, {
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
  const uids = itemsSelected.value.map(v => v.UserId);
  const req = await fetch(`/users?id=${uids.join(',')}`, {
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
