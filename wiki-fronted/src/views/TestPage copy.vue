
<template>
  <div style="position: relative">
    <div ref="editorRef" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import FluentEditor, {
  FULL_TOOLBAR,
  I18N,
  generateToolbarTip,
  generateTableUp,
  CollaborationModule,
} from '@opentiny/fluent-editor';
import '@opentiny/fluent-editor/style.css';
import '@opentiny/vue-theme/fluent-editor/index.css';

// emoji 表情
import data from '@emoji-mart/data';
import { computePosition } from '@floating-ui/dom';
import type { EmojiMartData } from '@emoji-mart/data';
import { Picker } from 'emoji-mart';

// table 表格
import {
  defaultCustomSelect,
  TableMenuContextmenu,
  TableSelection,
  TableUp,
} from 'quill-table-up';
import 'quill-table-up/index.css';
import 'quill-table-up/table-creator.css';

// toolbar-tip 工具栏提示
import QuillToolbarTip from 'quill-toolbar-tip';
import 'quill-toolbar-tip/dist/index.css';

// formula 可编辑公式
import type { MathliveModule } from '@opentiny/fluent-editor';
import 'mathlive';
import 'mathlive/static.css';
import 'mathlive/fonts.css';

// markdown 操作
import MarkdownShortcuts from 'quill-markdown-shortcuts';

// mind-map 思维导图
import SimpleMindMap from 'simple-mind-map';
import Drag from 'simple-mind-map/src/plugins/Drag.js';
import Export from 'simple-mind-map/src/plugins/Export.js';
import Themes from 'simple-mind-map-plugin-themes';
import nodeIconList from 'simple-mind-map/src/svg/icons';

// flow-chart 流程图
import LogicFlow from '@logicflow/core';
import { DndPanel, SelectionSelect, Snapshot } from '@logicflow/extension';

// syntax 语法高亮
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

// screenshot 截屏
import Html2Canvas from 'html2canvas';
window.Html2Canvas = Html2Canvas;

// 公式
import katex from 'katex';
import 'katex/dist/katex.min.css';
window.katex = katex;

// mention @提醒
const searchKey = 'name';
const mentionList = [
  {
    name: 'kagol',
    cn: '卡哥',
    followers: 156,
    avatar: 'https://avatars.githubusercontent.com/u/9566362?v=4',
  },
  {
    name: 'zzcr',
    cn: '超哥',
    followers: 10,
    avatar: 'https://avatars.githubusercontent.com/u/18521562?v=4',
  },
  {
    name: 'hexqi',
    cn: '小伍哥',
    followers: 2,
    avatar: 'https://avatars.githubusercontent.com/u/18585869?v=4',
  },
];

let editor: FluentEditor;
const editorRef = ref<HTMLElement>();

onMounted(() => {
  if (!editorRef.value) return;

  // 注册 Quill 模块
  FluentEditor.register(
    { 'modules/toolbar-tip': generateToolbarTip(QuillToolbarTip) },
    true
  );
  FluentEditor.register({ 'modules/table-up': generateTableUp(TableUp) }, true);
  FluentEditor.register('modules/markdownShortcuts', MarkdownShortcuts);
  FluentEditor.register(
    'modules/collaborative-editing',
    CollaborationModule,
    true
  );

  // 初始化语言
  const lang = ref('zh-CN');

  editor = new FluentEditor(editorRef.value, {
    theme: 'snow',
    modules: {
      toolbar: {
        container: [...FULL_TOOLBAR, ['mind-map', 'flow-chart']],
        handlers: {
          formula(this: any) {
            const mathlive = this.quill.getModule('mathlive') as MathliveModule;
            mathlive.createDialog('e=mc^2');
          },
        },
      },
      file: true,
      markdownShortcuts: true,
      syntax: {
        hljs,
      },
      counter: true,
      mathlive: true,
      emoji: {
        emojiData: data as EmojiMartData,
        EmojiPicker: Picker,
        emojiPickerPosition: computePosition,
      },
      i18n: {
        lang: lang.value,
      },
      'toolbar-tip': {
        defaultTooltipOptions: {
          tipHoverable: false,
        },
      },
      'table-up': {
        customSelect: defaultCustomSelect,
        modules: [{ module: TableSelection }, { module: TableMenuContextmenu }],
      },
      'mind-map': {
        deps: {
          SimpleMindMap,
          Themes,
          Drag,
          Export,
          nodeIconList,
        },
      },
      'flow-chart': {
        deps: {
          LogicFlow,
          DndPanel,
          SelectionSelect,
          Snapshot,
        },
      },
      mention: {
        containerClass: 'ql-mention-list-container__custom-list',
        itemKey: 'cn',
        searchKey,
        search(term: string) {
          return mentionList.filter((item) => {
            return item[searchKey] && String(item[searchKey]).includes(term);
          });
        },
        renderMentionItem(item: any) {
          return `
            <div class="item-avatar">
              <img src="${item.avatar}">
            </div>
            <div class="item-info">
              <div class="item-name">${item.cn}</div>
              <div class="item-desc">${item.followers}粉丝</div>
            </div>
          `;
        },
      },
    },
  });
});
</script>


<style lang="less">
.ql-mention-list-container.ql-mention-list-container__custom-list
  .ql-mention-list
  .ql-mention-item {
  display: flex;
  align-items: center;
  height: 52px;
  line-height: 1.5;
  font-size: 12px;
  padding: 0 12px;

  &.ql-mention-item--active {
    background-color: #f1f2f3;
    color: #18191c;
  }

  .item-avatar {
    margin-right: 8px;

    img {
      width: 36px;
      border-radius: 50%;
    }
  }

  .item-info {
    .item-desc {
      color: #9499a0;
    }
  }
}
</style>
