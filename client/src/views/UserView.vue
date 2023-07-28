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
          <div><a @click="editItem(item)">Edit</a></div>
          <div><a @click="deleteItem(item)">Delete</a></div>
        </div>
      </template>
      <template #expand="item">
        <div>
          {{item.Note}}
        </div>
      </template>
    </EasyDataTable>
    
    <div v-if="edit_visible">
      <h3>Edit {{ editingItem.UserId }}:</h3>
      <div>
        <div>UserName:<input type="text" v-model="editingItem.UserName" /></div>
        <div>Note:<input type="text" v-model="editingItem.Note" /></div>
      </div>
      <div class="btns">
        <button>OK</button>
        <button @click="close_edit()"></button>
      </div>
    </div>
    
    <div v-if="delete_visible">
      <h3>Delete "{{ deletingItem.UserId }}"?</h3>
      <div class="btns">
        <button>OK</button>
        <button @click="close_delete()"></button>
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
  { text: 'UserName', value: 'UserName', sortable: true },
  { text: 'UserId', value: 'UserId', sortable: true },
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
  const req = await fetch('/users');
  if (req.status != 200) {
    return false;
  }
  const json = await req.json()
  const user = json.body;
  items.value = user.map((v: list) => fmt(v, ...field));
  loading.value = false;
  return true;
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
const close_edit = () => {
  edit_visible.value = false;
}

const deletingItem = reactive({
  UserId: ''
});
const deleteItem = (item: Item) => {
  deletingItem.UserId = item.UserId;
  delete_visible.value = true;
}
const close_delete = () => {
  delete_visible.value = false;
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
