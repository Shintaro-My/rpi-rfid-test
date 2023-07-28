<template>
  <div class="wrap">

    <EasyDataTable
      show-index
      v-model:items-selected="itemsSelected"
      buttons-pagination
      :headers="headers"
      :items="items"
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
const headers: Header[] = [
  { text: 'UserId', value: 'UserId' },
  { text: 'UserName', value: 'UserName' },
  { text: 'Note', value: 'Note' }
]
const itemsSelected: Ref<Item[]> = ref([]);
const items: Ref<Item[]> = ref([]);

const loading: Ref<boolean> = ref(false);

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
  items.value = user.map((v: list) => fmt(v, 'UserId', 'UserName', 'Note'));
  loading.value = false;
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
