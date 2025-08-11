<template>
  <div>
    <h1>股市涨跌音乐生成器</h1>
    <button @click="handlePlayMusic">播放音乐</button>
    <div v-if="playing">
      <h3>正在播放音乐...</h3>
    </div>
    <div v-if="notes.length > 0">
      <h3>生成的音符：</h3>
      <ul>
        <li v-for="(note, index) in notes" :key="index">
          {{ note.note }} - {{ note.duration }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import * as Tone from 'tone';

export default {
  name: 'StockTrendM',
  data() {
    return {
      notes: [], // 存储生成的音符
      sampler: null, // Tone.Sampler 实例
      playing: false, // 是否正在播放
      noteNames: [ // 88 个钢琴键的音符名称，从 A0 到 C8
        'A0','A#0','B0',
        'C1','C#1','D1','D#1','E1','F1','F#1','G1','G#1','A1','A#1','B1',
        'C2','C#2','D2','D#2','E2','F2','F#2','G2','G#2','A2','A#2','B2',
        'C3','C#3','D3','D#3','E3','F3','F#3','G3','G#3','A3','A#3','B3',
        'C4','C#4','D4','D#4','E4','F4','F#4','G4','G#4','A4','A#4','B4',
        'C5','C#5','D5','D#5','E5','F5','F#5','G5','G#5','A5','A#5','B5',
        'C6','C#6','D6','D#6','E6','F6','F#6','G6','G#6','A6','A#6','B6',
        'C7','C#7','D7','D#7','E7','F7','F#7','G7','G#7','A7','A#7','B7',
        'C8'
      ],
      noteFiles: {} // 音符对应的音频文件路径
    };
  },
  created() {
    // 初始化noteFiles，将每个音符名称映射到对应的音频文件路径
    this.noteNames.forEach(note => {
      this.noteFiles[note] = `/audio/piano-sounds/${note}.mp3`; // 假设音频文件放在 public/audio/piano-sounds/
    });
  },
  methods: {
    /**
     * 将“涨跌幅”映射到具体的钢琴键
     * @param {number} change - 涨跌幅度
     * @returns {string} - 对应的音符名称
     */
    mapChangeToNote(change) {
      const minChange = -20;
      const maxChange = 20;
      const totalRange = maxChange - minChange; // 总范围40%
      const keyRange = this.noteNames.length; // 88个键
      const changeClamped = Math.max(minChange, Math.min(maxChange, change)); // 限制涨跌幅度在[-20, 20]之间
      const normalized = (changeClamped - minChange) / totalRange; // 归一化到0到1之间
      const keyIndex = Math.floor(normalized * (keyRange - 1)); // 计算对应的键索引，0到87
      return this.noteNames[keyIndex];
    },
    
    /**
     * 将“涨跌幅”映射到按键持续时间
     * @param {number} change - 涨跌幅度
     * @returns {string} - Tone.js支持的持续时间字符串，如 '4n', '8n'
     */
    mapChangeToDuration(change) {
      const absChange = Math.abs(change);
      const durationValue = Math.min(absChange / 0.25, 8); // 最大持续时间为8分音符
      
      // 根据持续时间值映射到Tone.js支持的持续时间字符串
      if (durationValue <= 1) return '16n';
      if (durationValue <= 2) return '8n';
      if (durationValue <= 4) return '4n';
      if (durationValue <= 8) return '2n';
      return '1n';
    },
    
    /**
     * 根据传入的数据数组生成音符序列
     * @param {Array} dataArray - 包含“涨跌幅”的数组
     * @returns {Array} - 生成的音符和持续时间数组
     */
    generateNotesFromData(dataArray) {
      return dataArray.map(item => {
        const change = item['涨跌幅'];
        const note = this.mapChangeToNote(change);
        const duration = this.mapChangeToDuration(change);
        return { note, duration };
      });
    },
    
    /**
     * 初始化Tone.Sampler并加载所有音频文件
     */
    async initSampler() {
      try {
        this.sampler = new Tone.Sampler({
          urls: this.noteFiles,
          release: 1,
          baseUrl: '', // baseUrl已包含在noteFiles中
        }).toDestination();
        
        await this.sampler.loaded; // 等待所有样本加载完成
        console.log("Sampler 已加载所有音频文件");
      } catch (error) {
        console.error("Sampler 加载失败:", error);
      }
    },
    
    /**
     * 播放音乐的核心函数
     * @param {Array} dataArray - 包含“涨跌幅”的数组
     */
    async playMusic(dataArray) {
      if (!dataArray || !Array.isArray(dataArray)) {
        console.error("playMusic 函数需要一个数组作为参数");
        return;
      }
      
      // 生成音符序列
      this.notes = this.generateNotesFromData(dataArray);
      
      // 初始化Sampler（如果尚未初始化）
      if (!this.sampler) {
        await this.initSampler();
      }
      
      // 检查Sampler是否已加载完成
      if (!this.sampler || !this.sampler.loaded) {
        console.error("Sampler 未加载完成");
        return;
      }
      
      this.playing = true; // 设置播放状态为true
      
      // 创建一个Tone.Part来调度音符
      const now = Tone.now();
      const part = new Tone.Part((time, noteObj) => {
        this.sampler.triggerAttackRelease(noteObj.note, noteObj.duration, time);
      }, this.notes).start(now);
      
      // 设置节拍速度（BPM）
      Tone.Transport.bpm.value = 120; // 设置120 BPM
      
      // 启动Tone.Transport开始时间线
      Tone.Transport.start();
      
      // 计算总播放时间
      const totalDuration = this.notes.reduce((acc, note) => {
        return acc + Tone.Time(note.duration).toSeconds();
      }, 0);
      
      // 在音乐播放完成后停止Tone.Transport并清理Tone.Part
      setTimeout(() => {
        Tone.Transport.stop();
        part.dispose(); // 清理Tone.Part
        this.playing = false; // 设置播放状态为false
      }, (totalDuration + 1) * 1000); // 加1秒缓冲
    },
    
    /**
     * 处理播放音乐的按钮点击事件
     */
    handlePlayMusic() {
      const sampleData = [
        { '涨跌幅': 1.5 },
        { '涨跌幅': -3.2 },
        { '涨跌幅': 5.0 },
        { '涨跌幅': -2.1 },
        { '涨跌幅': 0.8 },
        { '涨跌幅': -0.5 }
      ];
      this.playMusic(sampleData);
    }
  }
};
</script>

<style scoped>
h1 {
  text-align: center;
  margin-top: 50px;
}

button {
  display: block;
  margin: 20px auto;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  font-size: 18px;
}
</style>
