<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <!--<img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />-->

    <div class="t_logo_wrap">
      <div class="t_logo"></div>
    </div>
    
    <div class="wrapper">
      <nav>
        <RouterLink to="/users">登録ユーザー</RouterLink>
        <RouterLink to="/anonymous">未登録ID</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

.t_logo_wrap {
  height: 150px;
  width: 150px;
}

.t_logo {
  --g_top: #42b883;
  --g_bottom: #42b883;
  --g_default: #364a5f;
  background: var(--g_default);
  background: linear-gradient(180deg,var(--g_top),var(--g_bottom) 64%,var(--g_default) 65% 100%);
  height: 100%;
  mask-image: url(@/assets/tsuden_logo_large_anim.svg);
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: 72%;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
