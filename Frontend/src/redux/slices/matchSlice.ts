import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// 对战记录类型
interface MatchRecord {
  match_id: number;
  challenger: {
    user_id: number;
    username: string;
    score: number;
    image_url: string;
  };
  opponent: {
    user_id: number;
    username: string;
    score: number;
    image_url: string;
  };
  result: 'Win' | 'Lose' | 'Tie';
  points_change: number;
  new_rating: number;
  matched_at: string;
}

// 对战状态接口
interface MatchState {
  currentMatch: MatchRecord | null;
  matchHistory: MatchRecord[];
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: MatchState = {
  currentMatch: null,
  matchHistory: [],
  loading: false,
  error: null,
};

// 创建Slice
const matchSlice = createSlice({
  name: 'match',
  initialState,
  reducers: {
    // 开始加载
    startLoading: (state) => {
      state.loading = true;
      state.error = null;
    },
    
    // 创建对战成功
    createMatchSuccess: (state, action: PayloadAction<MatchRecord>) => {
      state.currentMatch = action.payload;
      state.loading = false;
    },
    
    // 创建对战失败
    createMatchFailed: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    
    // 加载对战历史成功
    loadMatchHistorySuccess: (state, action: PayloadAction<MatchRecord[]>) => {
      state.matchHistory = action.payload;
      state.loading = false;
    },
    
    // 加载对战历史失败
    loadMatchHistoryFailed: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    
    // 清除当前对战
    clearCurrentMatch: (state) => {
      state.currentMatch = null;
    },
    
    // 清除错误信息
    clearError: (state) => {
      state.error = null;
    }
  }
});

// 导出actions
export const {
  startLoading,
  createMatchSuccess,
  createMatchFailed,
  loadMatchHistorySuccess,
  loadMatchHistoryFailed,
  clearCurrentMatch,
  clearError
} = matchSlice.actions;

// 导出reducer
export default matchSlice.reducer; 