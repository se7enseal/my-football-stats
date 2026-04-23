import { API_BASE_URL } from "./config";

function joinUrl(base, path) {
  if (!base) return path;
  if (base.endsWith("/") && path.startsWith("/")) return base.slice(0, -1) + path;
  if (!base.endsWith("/") && !path.startsWith("/")) return base + "/" + path;
  return base + path;
}

export function requestJson(path, query = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: joinUrl(API_BASE_URL, path),
      method: "GET",
      data: query,
      timeout: 20000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) return resolve(res.data);
        reject({ type: "http", statusCode: res.statusCode, data: res.data });
      },
      fail: (err) => reject({ type: "network", err }),
    });
  });
}

export const api = {
  health() {
    return requestJson("/api/health");
  },
  hotLeagues() {
    return requestJson("/api/leagues/hot");
  },
  fixtures({ date, league, status }) {
    const q = {};
    if (date) q.date = date;
    if (league) q.league = league;
    if (status) q.status = status;
    return requestJson("/api/fixtures", q);
  },
};

