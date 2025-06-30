<template>
  <el-button :type="type" :size="size" @click="goBack">
    <slot>返回</slot>
  </el-button>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'BackButton',
  props: {
    type: {
      type: String,
      default: 'default'
    },
    size: {
      type: String,
      default: 'default'
    },
    // 可选的回退步数
    steps: {
      type: Number,
      default: 1
    },
    // 可选的默认回退路径，如果无法回退则跳转到此路径
    fallbackPath: {
      type: String,
      default: '/'
    }
  },
  setup(props) {
    const router = useRouter()

    const goBack = () => {
      // 尝试使用window.history.length判断是否可以回退
      if (window.history.length > 1) {
        router.go(-props.steps)
      } else {
        // 如果无法回退，则跳转到默认路径
        router.push(props.fallbackPath)
      }
    }

    return {
      goBack
    }
  }
}
</script>

<style scoped>
/* 可以添加自定义样式 */
</style>
