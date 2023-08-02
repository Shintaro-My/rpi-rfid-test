<template>
  <div class="wrap">

    <h1>バックアップ（作成中）</h1>

    <a @click="update()">最新の情報に更新する</a>

    <EasyDataTable
      show-index
      buttons-pagination
      :headers="headers"
      :items="items"
      :loading="loading"
      alternating
    >
      <template #item-operation="item">
        <div class="operation-wrapper">
          <div><a @click="selectItem(item)">...</a></div>
        </div>
      </template>
      <template #expand="item">
        <div class="memo">
          <ul>
            <li v-for="v in (item?.children || [])">
              <span class="bold">{{ v.name }}</span>
              <span>{{ v.mountpoint ? `"${v.mountpoint}"` : 'null' }}</span>
            </li>
          </ul>
        </div>
        
      </template>
    </EasyDataTable>
    
    <div v-if="backup_visible" class="darkbox">
      <h3>Copy to "{{ selectedDisk.name }}"?</h3>
      <div class="btns">
        <button @click="_copy()">Copy</button>
        <button @click="close_backup()">Cancel</button>
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

interface Disk {
  name: string,
  mountpoint: null | string,
  children?: Disk[]
}

const headers: Header[] = [
  { text: 'name', value: 'name', sortable: true },
  { text: 'mount', value: 'mountpoint', sortable: true },
  { text: '_', value: 'operation' }
]
const items: Ref<Item[]> = ref([]);

const loading: Ref<boolean> = ref(false);

const backup_visible: Ref<boolean> = ref(false);

const update = async () => {
  loading.value = true;
  const req = await fetch('/lsblk');
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  const json = await req.json()
  const disks: Disk[] = json.body;
  items.value = disks;
  loading.value = false;
  return true;
}

const close_backup = () => {
  backup_visible.value = false;
}

const selectedDisk = reactive({
  name: ''
});
const selectItem = (item: Item) => {
  selectedDisk.name = item.name;
  backup_visible.value = true;
}
const _copy = async () => {
  loading.value = true;
  const { name } = selectedDisk;
  alert(name);
  /*
  const req = await fetch(`/users?id=${UserId}`, {
    method: 'DELETE'
  });
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  */
  close_backup();
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
@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
