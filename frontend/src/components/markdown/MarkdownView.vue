<script setup lang="ts">
import { VueMarkdownRenderer } from "vue-mdr";
import CodeBlockRenderer from "./CodeBlockRenderer.vue";

const { source, theme = "dark" } = defineProps<{
  source: string;
  theme?: "light" | "dark";
  stream?: boolean;
}>();
</script>

<template>
  <article
    class="prose prose-slate mx-auto my-10 max-w-none"
    :class="{ 'stream-wrapper': stream, 'prose-invert': theme === 'dark' }"
  >
    <VueMarkdownRenderer
      :source
      :theme
      :code-block-renderer="CodeBlockRenderer"
    ></VueMarkdownRenderer>
  </article>
</template>

<style>
.stream-wrapper > *,
.stream-wrapper .text-segmenter,
.stream-wrapper .shiki-stream span {
  animation: fade-in 0.5s ease-in-out;
}

@keyframes fade-in {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}
</style>
