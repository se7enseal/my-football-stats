<template>
  <view class="page">
    <view class="card">
      <view class="row">
        <picker mode="date" :value="date" @change="onPickDate">
          <view class="pill">日期：{{ date }}</view>
        </picker>
        <picker :range="leagueOptions" range-key="name" @change="onPickLeague">
          <view class="pill">联赛：{{ leagueName }}</view>
        </picker>
      </view>
      <view class="tip">回查建议：先选日期，再按联赛过滤。</view>
    </view>

    <view v-if="error" class="error">{{ error }}</view>
    <view v-if="loading" class="loading">加载中…</view>

    <scroll-view scroll-y class="list" v-else>
      <view v-if="fixtures.length === 0" class="empty">暂无数据</view>
      <view v-for="m in fixtures" :key="m.id" class="item" @click="openDetail(m)">
        <view class="top">
          <text class="league">{{ m.league.name }}</text>
          <text class="time">{{ m.kickoffTime.slice(11) }}</text>
          <text class="status">{{ m.status.text }}</text>
        </view>
        <view class="mid">
          <text class="t">{{ m.home.name }}</text>
          <text class="s">{{ (m.score.home === null ? '-' : m.score.home) + ' : ' + (m.score.away === null ? '-' : m.score.away) }}</text>
          <text class="t">{{ m.away.name }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { api } from "../../utils/api";

function pad(n) {
  return n < 10 ? `0${n}` : `${n}`;
}

function today() {
  const d = new Date();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export default {
  data() {
    return {
      date: today(),
      leagueId: "",
      leagueName: "热门联赛",
      leagueOptions: [{ id: "", name: "热门联赛" }],
      fixtures: [],
      loading: false,
      error: "",
    };
  },
  onLoad() {
    this.loadLeagues();
    this.refresh();
  },
  methods: {
    async loadLeagues() {
      try {
        const res = await api.hotLeagues();
        const leagues = (res && res.leagues) || [];
        this.leagueOptions = [{ id: "", name: "热门联赛" }].concat(leagues);
      } catch (e) {
        // ignore
      }
    },
    onPickDate(e) {
      this.date = e.detail.value;
      this.refresh();
    },
    onPickLeague(e) {
      const idx = Number(e.detail.value);
      const item = this.leagueOptions[idx];
      this.leagueId = item.id ? String(item.id) : "";
      this.leagueName = item.name || "热门联赛";
      this.refresh();
    },
    openDetail(m) {
      const payload = encodeURIComponent(JSON.stringify(m));
      uni.navigateTo({ url: `/pages/match/detail?m=${payload}` });
    },
    async refresh() {
      this.loading = true;
      this.error = "";
      try {
        const res = await api.fixtures({
          date: this.date,
          league: this.leagueId,
          status: "all",
        });
        this.fixtures = (res && res.fixtures) || [];
      } catch (e) {
        this.error = `加载失败：${e && e.message ? e.message : e}`;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 12px;
}
.card {
  background: #ffffff;
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 6px 18px rgba(17, 24, 39, 0.06);
}
.row {
  display: flex;
  gap: 10px;
}
.pill {
  padding: 8px 10px;
  background: #f3f4f6;
  border-radius: 10px;
  font-size: 12px;
}
.tip {
  margin-top: 10px;
  color: #6b7280;
  font-size: 12px;
}
.list {
  flex: 1;
  margin-top: 10px;
}
.item {
  background: #ffffff;
  border-radius: 14px;
  padding: 12px;
  margin-bottom: 10px;
  box-shadow: 0 6px 18px rgba(17, 24, 39, 0.06);
}
.top {
  display: flex;
  justify-content: space-between;
  color: #6b7280;
  font-size: 11px;
  margin-bottom: 8px;
}
.mid {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.t {
  width: 36%;
  font-weight: 700;
  font-size: 13px;
  color: #111827;
  text-align: center;
}
.s {
  width: 28%;
  text-align: center;
  font-weight: 900;
  font-size: 16px;
  color: #ef4444;
}
.empty,
.loading,
.error {
  padding: 12px;
  border-radius: 12px;
  background: #ffffff;
  color: #6b7280;
}
.error {
  background: #fff7ed;
  color: #9a3412;
}
</style>

