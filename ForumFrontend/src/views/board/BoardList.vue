<template>
  <div class="board-list-container">
    <el-card class="board-list-card">
      <template #header>
        <div class="clearfix">
          <span class="board-list-title">板块列表</span>
          <el-button
            v-if="isAdmin"
            style="float: right; padding: 3px 0"
            type="primary"
            text
            @click="handleCreateBoard"
          >
            <i class="el-icon-plus"></i> 新建板块
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="boardList"
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column
          prop="name"
          label="板块名称"
          width="180"
        >
          <template #default="scope">
            <div class="board-name">
              <i class="el-icon-s-grid"></i>
              <span>{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="description"
          label="板块描述"
        >
        </el-table-column>

        <el-table-column
          prop="posts_count"
          label="帖子数量"
          width="100"
          align="center"
        >
        </el-table-column>

        <el-table-column
          label="操作"
          width="150"
          align="center"
        >
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              text
              @click.stop="handleViewBoard(scope.row)"
            >
              查看
            </el-button>
            <el-button
              v-if="isAdmin"
              size="small"
              type="primary"
              text
              @click.stop="handleEditBoard(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="isAdmin"
              size="small"
              type="primary"
              text
              class="delete-btn"
              @click.stop="handleDeleteBoard(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑板块对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible="dialogVisible"
      width="500px"
    >
      <el-form
        ref="boardForm"
        :model="boardForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="板块名称" prop="name">
          <el-input v-model="boardForm.name" placeholder="请输入板块名称"></el-input>
        </el-form-item>
        <el-form-item label="板块描述" prop="description">
          <el-input
            v-model="boardForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入板块描述"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitBoardForm">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBoardList, createBoard, updateBoard, deleteBoard } from '@/api/board'
import { mapGetters } from 'vuex'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

export default defineComponent({
  name: 'BoardList',
  data() {
    return {
      boardList: [],
      loading: false,
      dialogVisible: false,
      dialogType: 'create',
      boardForm: {
        name: '',
        description: '',
        cover_image: null
      },
      rules: {
        name: [
          { required: true, message: '请输入板块名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入板块描述', trigger: 'blur' },
          { min: 5, max: 500, message: '长度在 5 到 500 个字符', trigger: 'blur' }
        ]
      },
      currentBoardId: null
    }
  },
  computed: {
    ...mapGetters(['isLoggedIn', 'isAdmin', 'currentUser']),
    dialogTitle() {
      return this.dialogType === 'create' ? '创建板块' : '编辑板块'
    }
  },
  created() {
    this.fetchBoardList()
  },
  methods: {
    // 获取板块列表
    async fetchBoardList() {
      this.loading = true
      try {
        log('开始获取板块列表...')
        const response = await getBoardList()
        log('板块列表响应:', response)

        if (response && response.status === 0 && response.data) {
          // 处理Django REST framework自定义响应格式
          log('使用status=0格式处理板块列表数据')
          this.boardList = response.data || []
        } else if (response && response.code === 0 && response.data) {
          // 处理另一种自定义响应格式
          log('使用code=0格式处理板块列表数据')
          this.boardList = response.data || []
        } else if (response && Array.isArray(response)) {
          // 直接返回数组的情况
          log('使用数组格式处理板块列表数据')
          this.boardList = response
        } else {
          console.error('获取板块列表失败:', response ? response.msg : '未知错误')
          this.boardList = [] // 如果获取失败，设置为空数组
        }
      } catch (error) {
        console.error('获取板块列表失败:', error)
        ElMessage.error('获取板块列表失败，请稍后再试')
        this.boardList = [] // 如果发生错误，设置为空数组
      } finally {
        this.loading = false
      }
    },

    // 行点击事件
    handleRowClick(row) {
      this.handleViewBoard(row)
    },

    // 查看板块
    handleViewBoard(board) {
      this.$router.push({ name: 'BoardDetail', params: { id: board.id } })
    },

    // 创建板块
    handleCreateBoard() {
      this.dialogType = 'create'
      this.boardForm = {
        name: '',
        description: ''
      }
      this.dialogVisible = true
    },

    // 编辑板块
    handleEditBoard(board) {
      this.dialogType = 'edit'
      this.currentBoardId = board.id
      this.boardForm = {
        name: board.name,
        description: board.description
      }
      this.dialogVisible = true
    },

    // 删除板块
    async handleDeleteBoard(board) {
      try {
        await this.$confirm(`确定要删除板块 "${board.name}" 吗?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await deleteBoard(board.id)
        console.log('删除板块响应:', response)
        if (response && (response.code === 0 || response.status === 0)) {
          ElMessage.success(response.msg || '删除成功')
          this.fetchBoardList()
        } else {
          ElMessage.error(response?.msg || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除板块失败:', error)
          ElMessage.error('删除板块失败')
        }
      }
    },

    // 提交表单
    submitBoardForm() {
      this.$refs.boardForm.validate(async (valid) => {
        if (valid) {
          try {
            let response
            if (this.dialogType === 'create') {
              response = await createBoard(this.boardForm)
            } else {
              response = await updateBoard(this.currentBoardId, this.boardForm)
            }

            console.log(this.dialogType === 'create' ? '创建板块响应:' : '更新板块响应:', response)
            if (response && (response.code === 0 || response.status === 0)) {
              ElMessage.success(response.msg || (this.dialogType === 'create' ? '创建成功' : '更新成功'))
              this.dialogVisible = false
              this.fetchBoardList()
            } else {
              ElMessage.error(response?.msg || (this.dialogType === 'create' ? '创建失败' : '更新失败'))
            }
          } catch (error) {
            console.error(this.dialogType === 'create' ? '创建板块失败:' : '更新板块失败:', error)
            ElMessage.error(this.dialogType === 'create' ? '创建板块失败' : '更新板块失败')
          }
        } else {
          return false
        }
      })
    }
  }
})
</script>

<style scoped>
.board-list-container {
  padding: 20px;
}

.board-list-card {
  margin-bottom: 20px;
}

.board-list-title {
  font-size: 18px;
  font-weight: bold;
}

.board-name {
  display: flex;
  align-items: center;
}

.board-name i {
  margin-right: 8px;
  color: #409EFF;
}

.delete-btn {
  color: #F56C6C;
}

.el-table {
  cursor: pointer;
}
</style>
