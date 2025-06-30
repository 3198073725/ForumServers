<template>
  <div class="post-create-container">
    <el-card class="post-form-card">
      <template #header>
        <div class="clearfix">
        <span>{{ isEdit ? '编辑帖子' : '发布新帖' }}</span>
      </div>
      </template>

      <el-form
        ref="formRef"
        :model="postForm"
        :rules="rules"
        label-width="80px"
        :validate-on-rule-change="false"
        @submit.prevent
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="postForm.title" placeholder="请输入帖子标题"></el-input>
        </el-form-item>

        <el-form-item label="板块" prop="board">
          <el-select
            v-model="postForm.board"
            placeholder="请选择板块"
            style="width: 100%"
            :disabled="isEdit && !isAdmin"
          >
            <el-option
              v-for="board in boardOptions"
              :key="board.value"
              :label="board.label"
              :value="board.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="内容" prop="content" :show-message="false">
          <rich-text-editor
            v-model="postForm.content"
            :disabled="false"
            @change="handleContentChange"
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="loading">
            {{ isEdit ? '保存修改' : '发布帖子' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import RichTextEditor from '@/components/RichTextEditor.vue'
import { createPost, updatePost, getPostDetail } from '@/api/post'
import { getBoardList } from '@/api/board'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

export default {
  name: 'PostCreate',
  components: {
    RichTextEditor
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const store = useStore()
    const formRef = ref(null)
    const loading = ref(false)
    const isEdit = ref(false)
    const postId = ref(null)
    const boardOptions = ref([])
    const refreshLatestPosts = inject('refreshLatestPosts', null)

    // 表单数据
    const postForm = reactive({
        title: '',
      content: '',
      board: ''
    })

    // 表单验证规则
    const rules = {
        title: [
          { required: true, message: '请输入帖子标题', trigger: 'blur' },
        { min: 3, max: 100, message: '标题长度应在3-100个字符之间', trigger: 'blur' }
      ],
      content: [
        { required: true, message: '请输入帖子内容', trigger: 'blur' }
        ],
        board: [
          { required: true, message: '请选择板块', trigger: 'change' }
      ]
    }

    // 计算属性：是否已登录
    const isLoggedIn = computed(() => store.getters.isLoggedIn)
    
    // 计算属性：是否为管理员
    const isAdmin = computed(() => {
      const user = store.state.user
      return user && user.role === 'admin'
    })

    // 刷新最新帖子列表
    const refreshPosts = () => {
      if (refreshLatestPosts) {
        refreshLatestPosts()
      } else {
        log('未找到刷新函数')
    }
    }

    // 初始化
    onMounted(async () => {
      log('发帖页面创建, 登录状态:', isLoggedIn.value, '认证状态:', isLoggedIn.value)

      // 检查是否已登录
      if (!isLoggedIn.value) {
        log('发帖页面检测到未登录，跳转到登录页面')
        ElMessage.warning('请先登录才能发布帖子')
        router.push({ name: 'Login', query: { redirect: '/post/create' } })
      return
    }

      log('发帖页面检测到已登录，继续加载页面')

    // 清除可能的成功消息提示
      ElMessage.closeAll()

    // 添加延时清除，确保异步请求完成后也不会显示消息
    setTimeout(() => {
        log('组件内延时清除消息')
        ElMessage.closeAll()
      }, 100)

      // 获取板块列表
      await fetchBoardList()

      // 检查是否为编辑模式
      if (route.params.id) {
        isEdit.value = true
        postId.value = route.params.id
        await fetchPostDetail(postId.value)
      }
    })

    // 获取板块列表
    const fetchBoardList = async () => {
      try {
        log('开始获取板块列表...')
        const response = await getBoardList()
        
        log('板块列表响应:', response)

        let boards = []
        if (response && response.status === 0 && response.data) {
          log('使用status=0格式处理板块列表数据')
          boards = response.data || []
        } else if (response && response.code === 0 && response.data) {
          log('使用code=0格式处理板块列表数据')
          boards = response.data || []
        } else if (response && Array.isArray(response)) {
          log('使用数组格式处理板块列表数据')
          boards = response
        } else {
          boards = []
        }
        
        // 如果不是管理员，过滤掉一些特殊板块
        if (!isAdmin.value) {
          log('非管理员用户，过滤掉推荐和精选板块')
          boards = boards.filter(board => {
            return !board.name.includes('推荐') && 
                   !board.name.includes('精选') && 
                   board.status !== 'hidden'
          })
        }
        
        // 转换为选项格式
        boardOptions.value = boards.map(board => ({
          value: board.id,
          label: board.name
        }))
        
        log('获取到的板块选项:', boardOptions.value)
        
        // 清除可能的成功消息提示
        setTimeout(() => {
          log('获取板块列表后延时清除消息')
          ElMessage.closeAll()
        }, 100)
        
      } catch (error) {
        console.error('获取板块列表失败:', error)
        ElMessage.error('获取板块列表失败，请稍后再试')
      }
    }

    // 获取帖子详情（编辑模式）
    const fetchPostDetail = async (id) => {
      try {
        loading.value = true
        const response = await getPostDetail(id)
        
        if (response && response.data) {
          const post = response.data
          postForm.title = post.title
          postForm.content = post.content
          postForm.board = post.board?.id || ''
        } else {
          ElMessage.error('获取帖子详情失败')
          router.push('/posts')
        }
      } catch (error) {
        console.error('获取帖子详情失败:', error)
        ElMessage.error('获取帖子详情失败，请稍后再试')
        router.push('/posts')
      } finally {
        loading.value = false
      }
    }

    // 提交表单
    const submitForm = async () => {
      log('开始提交表单，当前表单数据:', postForm);
      
      if (!formRef.value) {
        ElMessage.error('表单引用不存在')
        return
      }
      
      try {
        // 表单验证
        await formRef.value.validate((valid, fields) => {
          log('表单验证结果:', valid, '验证失败字段:', fields);
        
          if (!valid) {
            throw new Error('表单验证失败')
          }
        })
        
        // 显示加载状态
        loading.value = true
        
        // 准备提交数据
        const postData = {
          title: postForm.title,
          content: postForm.content,
          board: postForm.board
        }
        
        // 根据是否为编辑模式调用不同API
        let response
        if (isEdit.value) {
          response = await updatePost(postId.value, postData)
              } else {
          response = await createPost(postData)
              }
              
        log('提交帖子响应:', response);

        // 处理响应
        if (response && (response.status === 0 || response.code === 0 || response.id)) {
          log('发布成功，完整响应对象:', {
                  response,
            status: response.status,
            code: response.code,
            id: response.id,
            data: response.data
                });
          
          // 显示成功消息
          ElMessage({
            message: isEdit.value ? '编辑帖子成功' : '发布帖子成功',
            type: 'success'
          })

                // 获取帖子ID
          let newPostId
          if (isEdit.value) {
            newPostId = postId.value
          } else if (response.data && response.data.id) {
            newPostId = response.data.id
          } else if (response.id) {
            newPostId = response.id
          } else if (typeof response === 'object') {
            // 尝试从响应对象中找到id字段
            for (const key in response) {
              if (key === 'id' && response[key]) {
                newPostId = response[key]
                break
              } else if (response[key] && typeof response[key] === 'object' && response[key].id) {
                newPostId = response[key].id
                break
                    }
                  }
                }

          log('解析后的帖子ID:', newPostId);
          
          // 刷新首页最新帖子列表
          try {
            refreshPosts()
            log('已刷新最新帖子列表');
          } catch (error) {
            console.error('刷新帖子列表失败:', error)
          }
          
          // 跳转到帖子详情页或板块页面
          if (newPostId) {
            router.push(`/posts/${newPostId}`)
          } else if (postForm.board) {
            const boardId = postForm.board
            log('跳转到板块详情页，板块ID:', boardId);
            router.push(`/boards/${boardId}`)
                } else {
            router.push('/posts')
                }
              } else {
          throw new Error(response?.msg || '操作失败')
              }
            } catch (error) {
        console.error('提交表单失败:', error)
        
        if (error.message === '表单验证失败') {
          log('表单验证失败');
          ElMessage.error('请检查表单填写是否正确')
        } else {
          ElMessage.error(error.message || '操作失败，请稍后再试')
        }
      } finally {
        loading.value = false
        }
    }

    // 处理内容变化
    const handleContentChange = (content) => {
      log('内容变化:', content);
      postForm.content = content
    }

    // 返回上一页
    const goBack = () => {
      router.back()
    }

    return {
      formRef,
      postForm,
      rules,
      loading,
      isEdit,
      boardOptions,
      submitForm,
      handleContentChange,
      goBack
    }
  }
}
</script>

<style scoped>
.post-create-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.post-form-card {
  margin-bottom: 20px;
}

:deep(.el-form-item__content) {
  line-height: normal;
}
</style>
