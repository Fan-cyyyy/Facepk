import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// 评分记录类型
interface ScoreRecord {
  score_id: number;
  user_id: number;
  face_score: number;
  image_url: string;
  feature_data?: any;
  scored_at: string;
  is_public: boolean;
}

export interface UserScores {
  rated: number;
  received: number;
  averageScore: number;
  winRate: number;
  battles: number;
  ranking: number | null;
}

// 评分状态接口
export interface ScoreState {
  scores: Record<string, number>;
  userScores: UserScores | null;
  currentScore: number | null;
  uploadProgress: number;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: ScoreState = {
  scores: {},
  userScores: null,
  currentScore: null,
  uploadProgress: 0,
  loading: false,
  error: null
};

// 创建Slice
export const scoreSlice = createSlice({
  name: 'score',
  initialState,
  reducers: {
    // 开始加载
    startLoading: (state) => {
      state.loading = true;
      state.error = null;
    },
    
    // 上传进度更新
    updateUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload;
    },
    
    // 评分成功
    scoreSuccess: (state, action: PayloadAction<ScoreRecord>) => {
      state.currentScore = action.payload.score_id;
      state.loading = false;
      state.uploadProgress = 0;
    },
    
    // 评分失败
    scoreFailed: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
      state.uploadProgress = 0;
    },
    
    // 不再使用scoreHistory
    loadScoreHistorySuccess: (state, action: PayloadAction<any[]>) => {
      // state.scoreHistory = action.payload; // 已移除
      state.loading = false;
    },
    
    // 不再使用scoreHistory
    loadScoreHistoryFailed: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    
    // 清除当前评分
    clearCurrentScore: (state) => {
      state.currentScore = null;
    },
    
    // 清除错误信息
    clearError: (state) => {
      state.error = null;
    },

    setScores: (state, action: PayloadAction<Record<string, number>>) => {
      state.scores = action.payload;
    },
    addScore: (state, action: PayloadAction<{userId: string, score: number}>) => {
      const { userId, score } = action.payload;
      state.scores[userId] = score;
    },
    setUserScores: (state, action: PayloadAction<UserScores>) => {
      state.userScores = action.payload;
    },
    setCurrentScore: (state, action: PayloadAction<number>) => {
      state.currentScore = action.payload;
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    }
  }
});

// 导出actions
export const {
  startLoading,
  updateUploadProgress,
  scoreSuccess,
  scoreFailed,
  loadScoreHistorySuccess,
  loadScoreHistoryFailed,
  clearCurrentScore,
  clearError,
  setScores,
  addScore,
  setUserScores,
  setCurrentScore,
  setUploadProgress,
  setLoading,
  setError
} = scoreSlice.actions;

// 导出reducer
export default scoreSlice.reducer; 