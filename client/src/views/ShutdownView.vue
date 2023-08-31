<template>
  <div class="wrap">

    <div class="btns">
      <button @click="lock() && shutdown('h', 'now')" v-bind:disabled="shutdown_now">
        シャットダウン
      </button>
    </div>
    <p>シャットダウンを押すと、ボード上の緑色LEDが点滅を開始します。</p>
    <p>点滅が終わるまで、電源を抜かないでください。</p>
  </div>
</template>

<script setup lang="ts">
import { defineComponent, ref, reactive } from "vue";
import type { Ref } from "vue";
import type { Header, Item } from "vue3-easy-data-table";
defineProps<{
  msg: string
}>()

const shutdown_now: Ref<boolean> = ref(false);
const lock = () => (shutdown_now.value = true);

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
const shutdown =async (mode: string, time: number | string | null = null) => {
  const req = await fetch(`/shutdown?mode=${mode}` + (time == null ? '' : `&time=${time}`), {
    method: 'DELETE'
  })
  console.log(await req.json());
}

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
