import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import scoreReducer from './slices/scoreSlice';
import matchReducer from './slices/matchSlice';

// 配置Redux存储
export const store = configureStore({
  reducer: {
    auth: authReducer,
    score: scoreReducer,
    match: matchReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

// 导出类型
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 