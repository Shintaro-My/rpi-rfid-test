<template>
  <div class="wrap">

    <EasyDataTable
      show-index
      v-model:items-selected="user_itemsSelected"
      buttons-pagination
      :headers="user_headers"
      :items="user_items"
      :loading="loading"
    >
    </EasyDataTable>
    
    <EasyDataTable
      show-index
      v-model:items-selected="anonymous_itemsSelected"
      buttons-pagination
      :headers="anonymous_headers"
      :items="anonymous_items"
      :loading="loading"
    >
    </EasyDataTable>

  </div>
</template>

<script setup lang="ts">
import { defineComponent, ref, reactive } from "vue";
import type { Ref } from "vue";
import type { Header, Item } from "vue3-easy-data-table";
defineProps<{
  msg: string
}>()
const user_headers: Header[] = [
  { text: 'UserId', value: 'UserId' },
  { text: 'UserName', value: 'UserName' },
  { text: 'Note', value: 'Note' }
]
const user_itemsSelected: Ref<Item[]> = ref([]);
const user_items: Ref<Item[]> = ref([]);

const anonymous_headers: Header[] = [
  { text: 'UserId', value: 'UserId' },
  { text: 'LastaUpdate', value: 'LastaUpdate' }
]
const anonymous_itemsSelected: Ref<Item[]> = ref([]);
const anonymous_items: Ref<Item[]> = ref([]);

const loading: Ref<boolean> = ref(false);

type list = (string | number)[];
const fmt = (ary: list, ...label: string[]) => {
  const obj: { [name: string]: string | number } = {};
  for (let i = 0; i < ary.length; i++) {
    const key = label[i]
    obj[key] = ary[i]
  }
}
const update = async () => {
  loading.value = true;
  const reqs = await Promise.all(['/users', '/anonymous'].map(u => fetch(u)));
  if (reqs.find(r => r.status != 200)) {
    return false;
  }
  const json = await Promise.all(reqs.map(r => r.json()));
  const [user, anonymous] = json.map(v => v.body);
  user_items.value = user.map((v: list) => fmt(v, 'UserId', 'UserName', 'Note'));
  anonymous_items.value = anonymous.map((v: list) => fmt(v, 'UserId', 'LastUpdate'));
  loading.value = false;
  console.log(user_items);
  return true;
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
