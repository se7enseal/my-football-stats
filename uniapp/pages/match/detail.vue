<template>
  <view class="page">
    <view class="card">
      <view class="league">{{ m.league.name }}</view>
      <view class="title">
        <text class="team">{{ m.home.name }}</text>
        <text class="score">{{ scoreText }}</text>
        <text class="team">{{ m.away.name }}</text>
      </view>
      <view class="sub">
        <text>{{ m.kickoffTime }}</text>
        <text class="dot">·</text>
        <text>{{ m.status.text }}<text v-if="m.status.minute"> {{ m.status.minute }}'</text></text>
      </view>
    </view>

    <view class="hint">
      详情页已能展示列表带来的信息。后端补齐单场详情接口后，这里可以继续加入事件/统计/阵容。
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      m: {
        league: { name: "" },
        home: { name: "" },
        away: { name: "" },
        score: { home: null, away: null },
        kickoffTime: "",
        status: { text: "" },
      },
    };
  },
  computed: {
    scoreText() {
      const h = this.m.score.home === null ? "-" : this.m.score.home;
      const a = this.m.score.away === null ? "-" : this.m.score.away;
      return `${h} : ${a}`;
    },
  },
  onLoad(query) {
    try {
      if (query && query.m) this.m = JSON.parse(decodeURIComponent(query.m));
    } catch (e) {
      // ignore
    }
  },
};
</script>

<style scoped>
.page {
  padding: 12px;
}
.card {
  background: #ffffff;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 6px 18px rgba(17, 24, 39, 0.06);
}
.league {
  color: #6b7280;
  font-size: 12px;
  margin-bottom: 10px;
}
.title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.team {
  width: 35%;
  font-weight: 700;
  font-size: 14px;
  color: #111827;
  text-align: center;
}
.score {
  width: 30%;
  text-align: center;
  font-weight: 900;
  font-size: 18px;
  color: #ef4444;
}
.sub {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  gap: 8px;
  color: #6b7280;
  font-size: 12px;
}
.dot {
  color: #d1d5db;
}
.hint {
  margin-top: 12px;
  padding: 12px;
  background: #ffffff;
  border-radius: 14px;
  color: #6b7280;
  font-size: 12px;
}
</style>

