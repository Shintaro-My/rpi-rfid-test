<template>
  <div class="wrap">

    <h1>バックアップ</h1>

    <h3>接続中のストレージ</h3>
    <a @click="update()">最新の情報に更新する</a>
    <EasyDataTable
      show-index
      buttons-pagination
      :headers="headers"
      :items="items"
      :loading="loading"
      alternating
    >
      <template #item-mountpoint="item">
        <span class="code" v-for="v in splitter(item.mountpoint)">
          {{ v }}
        </span>
      </template>
      <template #item-operation="item">
        <div class="operation-wrapper">
          <div v-if="!isBaseMount(item.mountpoint)">
            <a @click="selectItem(item)">選択</a>
          </div>
        </div>
      </template>
      <template #expand="item">
        <div class="memo">
          <span class="bold">パーティション</span>
          <div class="tbl">
            <template v-for="v in (item?.children || [])">
              <span class="bold">{{ v.name }}</span>
              <span>
                <span class="code">{{ v.mountpoint ? `"${v.mountpoint}"` : 'null' }}</span>
              </span>
            </template>
          </div>
        </div>
        
      </template>
    </EasyDataTable>
    

    <div class="btns">
      <button @click="get_stream()" v-bind:disabled="ws_active || !selectedDisk.name">
        {{ selectedDisk.name ? `"${selectedDisk.name}"にバックアップ` : '選択されていません' }}
      </button>
    </div>
    <div class="cmd_block">
      <div class="stdout_line" v-for="line in server_stdout">
        {{ line }}
      </div>
      <div class="endline" v-bind:class="{ active: ws_active }" ref="scrollAnchor"></div>
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

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const time_format = Intl.DateTimeFormat("ja-JP", {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

const headers: Header[] = [
  { text: 'name', value: 'name', sortable: true },
  { text: 'mount', value: 'mountpoint', sortable: true },
  { text: '_', value: 'operation' }
]
const items: Ref<Item[]> = ref([]);

const loading: Ref<boolean> = ref(false);

const scrollAnchor: Ref<HTMLDivElement | null> = ref(null);
const scrollCmdBottom = async () => {
  await sleep(100);
  scrollAnchor.value?.scrollIntoView({ behavior: 'smooth', block: 'end' });
};

interface StdOut {
  data: string,
  type: string
}
const ws_active: Ref<boolean> = ref(false);
const server_stdout: Ref<string[]> = ref([]);
const backupChecker = async () => {
  let first = true;
  while (true) {
    if (first) {
      first = false;
      await sleep(100);
    } else {
      await sleep(5000);
    }
    const { status } = await fetch('/backup');
    if (!scrollAnchor.value) {
      break;
    }
    if (status == 401) {
      server_stdout.value = [...server_stdout.value, `${time_format.format(new Date())}: Backup in progress...`];
      scrollCmdBottom();
    }
    else if (status == 200) {
      server_stdout.value = [...server_stdout.value, `${time_format.format(new Date())}: Ready.`];
      scrollCmdBottom();
      break;
    }
    else {
      server_stdout.value = [...server_stdout.value, `${time_format.format(new Date())}: Communication failed.`];
      scrollCmdBottom();
      break;
    }
  }
}
const get_stream = async () => {
  if (!selectedDisk.name) return alert('保存先が選択されていません。');
  const check = await fetch('/backup');
  if (check.status != 200) {
    if (check.status == 401) {
      alert('バックアップが既に進行中です。');
      return false;
    }
    alert('Communication failed.')
    return false;
  }

  const req = await fetch(`/backup?disk=${selectedDisk.name}`, {method: 'PUT'});
  if (req.status != 200) {
    if (req.status == 401) {
      alert('バックアップが既に進行中です。');
      return false;
    }
    alert('Communication failed.')
    return false;
  }
  const { body } = await req.json();
  server_stdout.value = [body];

  await backupChecker();
  /*
  const ws = new WebSocket(url);
  console.log(url, ws);
  ws.onopen = e => {
    console.log(e);
    server_stdout.value = [];
    ws_active.value = true;
  };
  ws.onmessage = e => {
    const obj = JSON.parse(e.data);
    server_stdout.value = [...server_stdout.value, obj];
    scrollCmdBottom();
  }
  ws.onclose = e => {
    server_stdout.value = [...server_stdout.value, {data: '[END]', type: 'none'}];
    scrollCmdBottom();
    ws_active.value = false;
  }
  */
}

const splitter = (str: string) => str.split(',').filter((s: string) => s).map((s: string) => `"${s}"`);
const isBaseMount = (str: string) => splitter(str).find(v => -1 < ['"/"', '"/boot"'].indexOf(v));
const update = async () => {
  loading.value = true;
  const req = await fetch('/lsblk');
  if (req.status != 200) {
    alert('Communication failed.')
    return false;
  }
  const json = await req.json()
  const disks: Disk[] = json.body;
  for (const v of disks) {
    v.mountpoint = (v.children || []).map(c => c.mountpoint).filter(s => s).join(',');
  }
  items.value = disks;
  loading.value = false;
  return true;
}

const selectedDisk = reactive({
  name: ''
});
const selectItem = (item: Item) => {
  selectedDisk.name = item.name;
}

update();
backupChecker();

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
.tbl {
  display: grid;
  grid-template-columns: auto 1fr;
}
.tbl > span {
    display: inline-flex;
    align-items: center;
}
.bold {
  font-weight: 700;
}
.bold::after {
  content: ':';
  font-weight: 700;
}
.code {
  background: #ddd;
  color: #555;
  display: inline-flex;
  font-family: Courier New,Courier,monospace;
  font-weight: bold;
  margin: .1em .5em;
  padding: .25em;
  border: 1px dashed;
  border-radius: 0.25em;
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
.cmd_block {
  background: #eee;
  border: 1px dashed;
  border-radius: 0.35em;
  color: #000;
  font-family: Courier New,Courier,monospace;
  font-size: .75em;
  font-weight: bold;
  height: 11em;
  margin: 0.5em 0;
  overflow: auto;
  padding: 0.5em 1em;
}
.stdout_line.cmd {
  background: #fff;
  border-radius: 0.35em;
  box-shadow: 1px 1px 2px #bbb;
  font-style: italic;
  margin: 0.5em 0;
  padding: 0.35em 0.75em;
}
.stdout_line.cmd::before {
  content: '$ ';
  color: #601;
  font-style: normal;
  font-weight: bold;
}
.stdout_line.stdout {
  font-weight: bold;
}
.stdout_line.none {
  color: #666;
}
.endline.active::before {
  animation: blink 1s linear infinite;
  content: '█';
  font-weight: bold;
}
@keyframes blink {
  0%,10% {
    opacity: 1;
  }
  40%,60% {
    opacity: 0;
  }
  90%,100% {
    opacity: 1;
  }
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
