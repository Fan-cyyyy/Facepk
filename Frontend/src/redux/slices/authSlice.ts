import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { User } from '../../hooks/useAuth';

// 定义认证状态接口
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  loading: false,
  error: null
};

// 创建Slice
export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // 开始认证过程
    startLoading: (state) => {
      state.loading = true;
      state.error = null;
    },
    
    // 登录成功
    login: (state, action: PayloadAction<User>) => {
      state.isAuthenticated = true;
      state.user = action.payload;
      state.loading = false;
      state.error = null;
    },
    
    // 登录失败
    loginFailed: (state, action: PayloadAction<string>) => {
      state.isAuthenticated = false;
      state.user = null;
      state.loading = false;
      state.error = action.payload;
    },
    
    // 登出
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.loading = false;
    },
    
    // 更新用户信息
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    
    // 设置加载状态
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    
    // 设置错误信息
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
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
  login, 
  loginFailed,
  logout, 
  setUser, 
  setLoading, 
  setError, 
  clearError 
} = authSlice.actions;

// 导出reducer
export default authSlice.reducer; 