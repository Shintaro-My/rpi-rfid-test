<template>
  <div class="wrap">

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
          <div><a @click="editItem(item)">Add as user</a></div>
          <div><a @click="deleteItem(item)">Delete</a></div>
        </div>
      </template>
    </EasyDataTable>
    
    <div v-if="edit_visible" class="darkbox">
      <h3>Add "<pre class="inline">{{ editingItem.UserId }}</pre>":</h3>
      <div>
        <div>UserName:<input type="text" v-model="editingItem.UserName" /></div>
        <div>Note:<input type="text" v-model="editingItem.Note" /></div>
      </div>
      <div class="btns">
        <button @click="_edit()">OK</button>
        <button @click="close_edit()">Cancel</button>
      </div>
    </div>

    <div v-if="delete_visible" class="darkbox">
      <h3>Delete "{{ deletingItem.UserId }}"?</h3>
      <div class="btns">
        <button @click="_delete()">OK</button>
        <button @click="close_delete()">Cancel</button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { defineComponent, ref, reactive } from "vue";
import type { Ref } from "vue";
import type { Header, Item } from "vue3-easy-data-table";
defineProps<{
  msg: string
}>()
const headers: Header[] = [
  { text: 'UserId', value: 'UserId', sortable: true },
  { text: 'LastUpdate', value: 'LastUpdate', sortable: true },
  { text: '_', value: 'operation' }
]
const itemsSelected: Ref<Item[]> = ref([]);
const items: Ref<Item[]> = ref([]);

const loading: Ref<boolean> = ref(false);

const edit_visible: Ref<boolean> = ref(false);
const delete_visible: Ref<boolean> = ref(false);

const field = ['UserId', 'UserName', 'Note'];

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
  const req = await fetch('/anonymous');
  if (req.status != 200) {
    return false;
  }
  const json = await req.json()
  const user = json.body;
  items.value = user.map((v: list) => fmt(v, 'UserId', 'LastUpdate'));
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
  UserId: '',
  UserName: '',
  Note: ''
});
const editItem = (item: Item) => {
  const { UserId } = item;
  editingItem.UserId = UserId;
  editingItem.UserName = '';
  editingItem.Note = '';
  edit_visible.value = true;
}
const _edit = async () => {
  loading.value = true;
  const { UserId, UserName, Note } = editingItem;
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
  const req = await fetch(`/anonymous?id=${UserId}`, {
    method: 'DELETE'
  });
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  close_delete();
  await update();
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

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
