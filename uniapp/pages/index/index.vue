<template>
  <view class="page">
    <view class="toolbar">
      <view class="row">
        <picker mode="date" :value="date" @change="onPickDate">
          <view class="pill">日期：{{ date }}</view>
        </picker>

        <picker :range="leagueOptions" range-key="name" @change="onPickLeague">
          <view class="pill">联赛：{{ leagueName }}</view>
        </picker>
      </view>

      <view class="tabs">
        <view class="tab" :class="{ active: status === 'all' }" @click="setStatus('all')">全部</view>
        <view class="tab" :class="{ active: status === 'live' }" @click="setStatus('live')">进行中</view>
        <view class="tab" :class="{ active: status === 'ns' }" @click="setStatus('ns')">未开赛</view>
        <view class="tab" :class="{ active: status === 'ft' }" @click="setStatus('ft')">完场</view>
        <view class="tab link" @click="goHistory">回查</view>
      </view>
    </view>

    <view v-if="error" class="error">{{ error }}</view>
    <view v-if="loading" class="loading">加载中…</view>

    <scroll-view scroll-y class="list" v-else>
      <view v-if="fixtures.length === 0" class="empty">暂无比赛</view>

      <view v-for="m in fixtures" :key="m.id" class="card" @click="openDetail(m)">
        <view class="meta">
          <text class="league">{{ m.league.name }}</text>
          <text class="time">{{ m.kickoffTime.slice(11) }}</text>
          <text class="status">{{ m.status.text }}<text v-if="m.status.minute"> {{ m.status.minute }}'</text></text>
        </view>

        <view class="teams">
          <view class="team">
            <image class="logo" :src="m.home.logo" mode="aspectFit" />
            <text class="name">{{ m.home.name }}</text>
          </view>

          <view class="score">
            <text class="s">{{ m.score.home === null ? '-' : m.score.home }}</text>
            <text class="dash">:</text>
            <text class="s">{{ m.score.away === null ? '-' : m.score.away }}</text>
          </view>

          <view class="team right">
            <image class="logo" :src="m.away.logo" mode="aspectFit" />
            <text class="name">{{ m.away.name }}</text>
          </view>
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
      status: "all",
      leagueId: "",
      leagueName: "热门联赛",
      leagueOptions: [{ id: "", name: "热门联赛" }],
      fixtures: [],
      loading: false,
      error: "",
      timer: null,
    };
  },
  onLoad() {
    this.loadLeagues();
    this.refresh();
  },
  onShow() {
    this.setupAutoRefresh();
  },
  onHide() {
    this.teardownAutoRefresh();
  },
  onUnload() {
    this.teardownAutoRefresh();
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
    setStatus(s) {
      this.status = s;
      this.refresh();
      this.setupAutoRefresh();
    },
    goHistory() {
      uni.navigateTo({ url: "/pages/history/index" });
    },
    openDetail(m) {
      // 详情接口后续补齐时可直接用 id 拉取更多数据
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
          status: this.status,
        });
        this.fixtures = (res && res.fixtures) || [];
      } catch (e) {
        this.error = `加载失败：${e && e.message ? e.message : e}`;
      } finally {
        this.loading = false;
      }
    },
    setupAutoRefresh() {
      this.teardownAutoRefresh();
      if (this.status !== "live") return;
      this.timer = setInterval(() => {
        this.refresh();
      }, 30000);
    },
    teardownAutoRefresh() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
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
}
.toolbar {
  padding: 12px 12px 8px;
  background: #ffffff;
  border-bottom: 1px solid #eef0f4;
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
.tabs {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  align-items: center;
}
.tab {
  padding: 6px 10px;
  border-radius: 10px;
  background: #f3f4f6;
  font-size: 12px;
}
.tab.active {
  background: #111827;
  color: #ffffff;
}
.tab.link {
  margin-left: auto;
  background: #e0f2fe;
  color: #075985;
}
.list {
  flex: 1;
}
.card {
  margin: 10px 12px;
  background: #ffffff;
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 6px 18px rgba(17, 24, 39, 0.06);
}
.meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 10px;
}
.teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.team {
  width: 38%;
  display: flex;
  align-items: center;
  gap: 8px;
}
.team.right {
  justify-content: flex-end;
  text-align: right;
}
.logo {
  width: 22px;
  height: 22px;
}
.name {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
}
.score {
  width: 24%;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 6px;
  font-weight: 800;
  color: #ef4444;
}
.s {
  font-size: 18px;
}
.dash {
  font-size: 14px;
  color: #9ca3af;
}
.empty,
.loading,
.error {
  margin: 18px 12px;
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

