<template>
  <el-avatar 
    :size="size" 
    :src="processedAvatarUrl" 
    @error="handleError"
  >
    {{ fallbackText }}
  </el-avatar>
</template>

<script>
import { computed } from 'vue'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

export default {
  name: 'UserAvatar',
  props: {
    user: {
      type: Object,
      required: true
    },
    size: {
      type: [Number, String],
      default: 'default'
    }
  },
  setup(props) {
    // 处理头像URL，确保使用完整路径
    const processedAvatarUrl = computed(() => {
      const avatarUrl = props.user?.avatar_url
      if (!avatarUrl) return ''
      
      // 如果已经是完整URL，直接返回
      if (avatarUrl.startsWith('http')) {
        return avatarUrl
      }
      
      // 否则添加后端服务器地址
      return `http://localhost:8000${avatarUrl}`
    })

    // 获取用于显示的文本（用户昵称或用户名的首字母）
    const fallbackText = computed(() => {
      if (!props.user) return 'U'
      return props.user.nickname?.charAt(0) || props.user.username?.charAt(0) || 'U'
    })

    // 处理头像加载错误
    const handleError = () => {
      log('头像加载失败，使用文字替代')
    }

    return {
      processedAvatarUrl,
      fallbackText,
      handleError
    }
  }
}
</script>

<style scoped>
/* 可以添加自定义样式 */
</style>
