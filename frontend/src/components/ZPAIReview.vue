<template>
  <div class="container">
    <div class="output" ref="output">
      <!-- 使用 v-html 渲染解析后的 Markdown HTML 内容 -->
      <div v-html="responseText"></div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      responseText: '', // 展示的原始 Markdown 文本
      loaded:false
    };
  },
  methods: {
    async fetchReplay() {
      if (this.loaded) {
        return;
      }
      this.responseText = ''; // 清空之前的响应内容

      try {
        // 使用 fetch 发起请求
        const response = await fetch("http://127.0.0.1:8088/api/ai-review"); // 替换为你的流式接口路径

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 获取流式数据
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        const readStream = async () => {
          let reading = true; // 用一个变量控制循环

          while (reading) {
            const { done, value } = await reader.read();
            if (done) {
              this.loaded = true;
              reading = false; // 设置循环结束条件
              break;
            }

            // 解码并逐段更新 Markdown 文本
            const newText = decoder.decode(value, { stream: true });

            // 实时追加到 responseText
            this.responseText += newText;

            // 确保光标总是在最底部
            this.scrollToBottom();
          }
        };

        await readStream();
      } catch (error) {
        console.error("流式请求错误:", error);
        this.responseText = "请求失败，请稍后重试。";
      } finally {
        this.copyToClipboard(this.responseText);
      }
    },

    // 将内容复制到剪切板
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        console.log("内容已复制到剪切板");
      }).catch(err => {
        console.error("复制失败:", err);
      });
    },

    // 将滚动条移动到最底部
    scrollToBottom() {
      this.$nextTick(() => {
        const outputDiv = this.$refs.output;
        if (outputDiv) {  // 确保 outputDiv 存在
          outputDiv.scrollTop = outputDiv.scrollHeight;
        }
      });
    }
  }
};
</script>

<style scoped>
.container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36vw;
  height: 68vh;
  background: #000000c8;
  color: #eaeaea;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  z-index: 99;
}

.output {
  font-size: 16px;
  line-height: 1.6;
  text-align: left;
  max-width: 100%;
  padding: 20px;
  white-space: pre-wrap; /* 保留空格和换行 */
  word-wrap: break-word; /* 单词超出时自动换行 */
  overflow: auto;
  max-height: 100%; /* 保证内容区填满 */
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: #555 #1e1e1e; /* Firefox */
}

/* 自定义滚动条（Webkit 浏览器） */
.output::-webkit-scrollbar {
  width: 6px; /* 设置滚动条宽度 */
}

.output::-webkit-scrollbar-thumb {
  background-color: #555; /* 滚动条滑块颜色 */
  border-radius: 3px;
}

.output::-webkit-scrollbar-track {
  background-color: #1e1e1e; /* 滚动条轨道颜色 */
}

.output h1 {
  font-size: 24px;
  margin-bottom: 16px;
}

.output h2 {
  font-size: 20px;
  margin-bottom: 12px;
}

.output p {
  margin-bottom: 10px;
}

.output ul {
  list-style-type: disc;
  margin-left: 20px;
}

.output code {
  background: #1e1e1e;
  color: #eaeaea;
  padding: 2px 4px;
  border-radius: 4px;
}

/* 控制按钮样式 */
.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #555;
  color: #eaeaea;
  border: none;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;
}

.close-btn:hover {
  background-color: #444;
}
</style>
