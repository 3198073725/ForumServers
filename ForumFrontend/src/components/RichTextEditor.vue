<template>
  <div class="rich-text-editor">
    <quill-editor
      v-model="content"
      :options="editorOption"
      @update:content="handleContentUpdate"
      @blur="handleBlur"
      :disabled="disabled"
      ref="quillEditor"
    />
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { defaultQuillOptions } from '@/utils/quill-config'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

export default {
  name: 'RichTextEditor',
  components: {
    QuillEditor
  },
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const content = ref(props.modelValue || '')
    const quillEditor = ref(null)

    const handleContentUpdate = (newContent) => {
      log('RichTextEditor - handleContentUpdate:', newContent);
      
      if (quillEditor.value && quillEditor.value.getQuill) {
        const quill = quillEditor.value.getQuill();
        const text = quill.getText().trim();
        const html = quill.root.innerHTML;
        
        log('RichTextEditor - 内容更新:', {
          html: html,
          text: text,
          isEmpty: !text
        });

        if (!text || text === '\n') {
          content.value = '';
          emit('update:modelValue', '');
          emit('change', '');
        } else {
          content.value = html;
          emit('update:modelValue', html);
          emit('change', html);
        }
      }
    }

    const handleBlur = () => {
      if (quillEditor.value && quillEditor.value.getQuill) {
        const quill = quillEditor.value.getQuill();
        const text = quill.getText().trim();
        const html = quill.root.innerHTML;
        
        log('RichTextEditor - 失去焦点:', {
          html: html,
          text: text,
          isEmpty: !text
        });

        if (!text || text === '\n') {
          content.value = '';
          emit('update:modelValue', '');
          emit('change', '');
        } else if (html !== content.value) {
          content.value = html;
          emit('update:modelValue', html);
          emit('change', html);
        }
      }
    }

    // 监听 modelValue 变化
    watch(() => props.modelValue, (newValue, oldValue) => {
      log('RichTextEditor - modelValue变化:', { 
        newValue, 
        oldValue, 
        contentValue: content.value 
      });
      
      if (newValue !== content.value) {
        content.value = newValue || '';
        
        // 如果编辑器已经初始化，手动更新内容
        if (quillEditor.value && quillEditor.value.getQuill) {
          log('手动更新Quill编辑器内容');
          const quill = quillEditor.value.getQuill();
          if (quill) {
            // 清空当前内容
            quill.setText('');
            // 设置新内容（如果是HTML格式）
            if (newValue && newValue.trim()) {
              quill.clipboard.dangerouslyPasteHTML(0, newValue);
            }
          }
        }
      }
    }, { immediate: true })

    onMounted(() => {
      log('RichTextEditor - 组件挂载，初始值:', props.modelValue);
      
      // 初始化时设置内容
      if (quillEditor.value) {
        log('RichTextEditor - 设置初始内容');
        
        try {
          const quill = quillEditor.value.getQuill();
          if (quill) {
            // 确保使用现代 API
            Object.assign(quill.options, {
              experimental: {
                useModernScrollingApi: true,
                useMutationObserver: true
              }
            });

            // 清空当前内容
            quill.setText('');
            // 设置新内容（如果是HTML格式）
            if (props.modelValue && props.modelValue.trim()) {
              quill.clipboard.dangerouslyPasteHTML(0, props.modelValue);
              content.value = props.modelValue;
              log('RichTextEditor - 初始内容设置成功');
            }
          }
        } catch (error) {
          console.error('RichTextEditor - 设置初始内容失败:', error);
        }
      }
    })

    return {
      content,
      editorOption: {
        ...defaultQuillOptions,
        readOnly: props.disabled
      },
      handleContentUpdate,
      handleBlur,
      quillEditor
    }
  }
}
</script>

<style scoped>
.rich-text-editor {
  width: 100%;
}

:deep(.ql-container) {
  min-height: 300px;
  font-size: 16px;
  line-height: 1.5;
}

:deep(.ql-editor) {
  min-height: 300px;
  padding: 12px 15px;
}

:deep(.ql-toolbar) {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  background-color: #f8f9fa;
}

:deep(.ql-container) {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

:deep(.ql-editor p) {
  margin-bottom: 1em;
}

:deep(.ql-editor img) {
  max-width: 100%;
  height: auto;
}

:deep(.ql-editor blockquote) {
  border-left: 4px solid #ccc;
  margin: 0;
  padding-left: 16px;
}

:deep(.ql-editor pre.ql-syntax) {
  background-color: #f8f9fa;
  border-radius: 4px;
  padding: 12px;
  margin: 8px 0;
}
</style> 