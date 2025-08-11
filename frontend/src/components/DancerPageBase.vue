<script>
export default {
  props: {
    totalBeats: {
      type: Number,
      required: true,
    },
    beatsPerData: {
      type: Number,
      default: 1, // 默认 1 个音频卡点对应一个数据点
    },
  },
  watch: {
    totalBeats(newVal) {
      if (newVal && this.fullData.length > 0) {
        this.internalTotalBeats = newVal; // Synchronize internal data
        this.computeDataPointsPerBeat();  // Recalculate data
      }
    },
    beatsPerData(newVal) {
      console.log("beatsPerData:" + newVal)
      if (newVal > 0) {
        this.computeDataPointsPerBeat();
      }
    },
  },
  data() {
    return {
      fullData: [],
      internalTotalBeats: this.totalBeats,
      chartOption: {},
      maxDisplayPoints: 66,
      dataPointsToDisplayAtBeat: [],
      displayDates: [],
      beatIndex: 0,
      direction: -2,
      firstAllShowed: true,
      beatCounter: 0,
    };
  },
  methods: {
    setMaxDisplayPoints(x){
      this.maxDisplayPoints = x;
    },
    isInnerControl() {
      return false;
    },
    setFullData(fd) {
      this.fullData = fd;
    },
    afterComputeDataPointsPerBeat(slice) {
      console.log(slice)
    },
    clearChartData() {
      throw new Error('clearChartData() must be implemented in the child component');
    },
    fullfillAllData() {
      throw new Error('fullfillAllData() must be implemented in the child component');
    },
    updateChartDataPoint(dataPoint) {
      throw new Error('updateChartDataPoint(' + dataPoint + ') must be implemented in the child component');
    },
    whenAllDataShowd() {
      if (this.isInnerControl()) {
        return;
      }
      const currentOption = this.$refs.chartInstance.getOption();
      if (this.firstAllShowed) {
        this.firstAllShowed = false;
        if (!currentOption.dataZoom || currentOption.dataZoom.length === 0) {
          this.$refs.chartInstance.setOption({
            dataZoom: [
              {
                type: 'slider',
                start: 0,
                end: 100
              },
              {
                type: 'inside',
                start: 0,
                end: 100
              }
            ]
          });
        }
        this.fullfillAllData();
      }
      if (currentOption.dataZoom) {
        let start = this.getZoomStart();
        if (start == 96) {
          this.direction = -2;
        }
        if (start == 0) {
          this.direction = 2;
        }
        this.setDataZoomRange(start + this.direction, 100);
      }
    },
    getZoomStart() {
      const currentOption = this.$refs.chartInstance.getOption();
      const currentStart = currentOption.dataZoom[0].start;
      return currentStart;
    },
    setDataZoomRange(start, end) {
      this.$refs.chartInstance.dispatchAction({
        type: 'dataZoom',
        start: start,
        end: end
      });
    },
    removeDataZoom() {
      const currentOption = this.$refs.chartInstance.getOption();

      if (currentOption.dataZoom && currentOption.dataZoom.length > 0) {

        this.$refs.chartInstance.setOption({
          dataZoom: []
        });
        console.log('dataZoom has been removed');
      } else {
        console.log('No dataZoom found, cannot remove');
      }
    },
    computeDataPointsPerBeat() {
      if (this.isInnerControl()) {
        return;
      }

      if (!this.internalTotalBeats || !this.fullData.length) {
        console.error("internalTotalBeats or fullData is not ready yet.");
        return;
      }

      const N_data = this.fullData.length;
      const N_beats = this.internalTotalBeats;

      if (N_beats <= 0) {
        console.error("Total beats must be greater than 0");
        return;
      }

      const N_beatPoints = Math.floor(N_beats / this.beatsPerData);
      let sliceCount = this.fullData.length;
      if (N_data >= N_beatPoints) {
        sliceCount = N_beatPoints;
      }
      console.log("N_data=" + N_data + ",N_beats=" + N_beats + ",sliceCount=" + sliceCount)
      this.dataPointsToDisplayAtBeat = this.fullData.slice(sliceCount * -1);
      this.afterComputeDataPointsPerBeat(sliceCount);
    },
    resetData(totalBeats) {
      try {
        this.clearChartData();
        if (!this.isInnerControl()) {
          this.firstAllShowed = false;
          this.internalTotalBeats = totalBeats;
          this.beatIndex = 0;
          this.beatCounter = 0; // Reset beat counter

          this.clearChartData();
          this.removeDataZoom();
          this.computeDataPointsPerBeat();
        }
      } catch (err) {
        console.log(err)
      }
    },
    stopUpdates() {
      console.log("==stopUpdates");
    },
    updateChartOnBeat() {

      try {
        this.beatCounter += 1;
        if (this.beatCounter % this.beatsPerData === 0) {

          if (!this.isInnerControl()) {
            if (!this.$refs.chartInstance) {
              return;
            }
            if (this.beatIndex >= this.dataPointsToDisplayAtBeat.length) {
              this.whenAllDataShowd();
            } else {
              const dataPoint = this.dataPointsToDisplayAtBeat[this.beatIndex];
              this.beatIndex += 1;
              this.addDataPoint(dataPoint);
            }
          } else {
            this.updateChartDataPoint(null);
          }
        }
      } catch (err) {
        console.log(err)
      }
    },
    addDataPoint(dataPoint) {
      if (!this.$refs.chartInstance) {
        return
      }
      this.updateChartDataPoint(dataPoint);

      this.$refs.chartInstance.setOption(this.chartOption);

      // Automatically show crosshair on the latest data point
      this.$nextTick(() => {
        const latestIndex = this.displayDates.length - 1;
        if (latestIndex >= 0) {
          this.$refs.chartInstance.dispatchAction({
            type: 'showTip',
            seriesIndex: 0, // Trigger tooltip of the first series
            dataIndex: latestIndex
          });
        }
      });
    },
  }
};
</script>