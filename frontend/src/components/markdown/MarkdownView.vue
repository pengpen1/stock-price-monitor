<script setup lang="ts">
import CodeBlockRenderer from "./CodeBlockRenderer.vue";
import MermaidRenderer from "./MermaidRenderer.vue";
import { createMarkdownRenderer } from "vue-mdr";

const VueMarkdownRenderer = createMarkdownRenderer({
  codeBlock: {
    renderer: CodeBlockRenderer,
  },
  mermaid: {
    renderer: MermaidRenderer,
  },
});

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
    <VueMarkdownRenderer :source :theme></VueMarkdownRenderer>
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
