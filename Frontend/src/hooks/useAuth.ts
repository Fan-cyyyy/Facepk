import { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { login as loginAction, logout as logoutAction, setUser } from '../redux/slices/authSlice';
import { RootState } from '../redux/store';
import { login as apiLogin, register as apiRegister, TokenResponse, UserResponse } from '../services/api';
import { AxiosResponse } from 'axios';

export interface User {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  nickname?: string;
}

export const useAuth = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, user, loading: authLoading } = useSelector((state: RootState) => state.auth);
  const [loading, setLoading] = useState(false);

  // 使用useCallback确保函数引用稳定
  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('token');
    console.log('检查认证状态, token:', token ? '存在' : '不存在');
    
    if (token) {
      try {
        // 尝试通过token获取用户信息
        // 在实际项目中应该实现一个获取用户信息的API
        // 这里我们先简单地模拟成功，后续可以完善
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        if (userData && userData.user_id) {
          dispatch(loginAction({
            id: userData.user_id,
            username: userData.username,
            email: userData.email || '',
            avatar: userData.avatar_url,
            nickname: userData.nickname
          }));
          return true;
        }
        return false;
      } catch (error) {
        console.error('验证token失败:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('userData');
        return false;
      }
    }
    return false;
  }, [dispatch]);

  // 应用启动时检查认证状态
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // 添加调试日志
  useEffect(() => {
    console.log('认证状态变化:', { isAuthenticated, user });
  }, [isAuthenticated, user]);

  const login = async (credentials: {username: string, password: string}) => {
    try {
      setLoading(true);
      console.log('开始登录流程:', credentials);
      
      // 调用API进行登录
      const response: AxiosResponse<TokenResponse> = await apiLogin(credentials.username, credentials.password);
      
      console.log('登录API返回响应:', response);
      
      // 正确访问response对象中的数据
      const responseData = response.data;
      
      if (responseData && responseData.access_token) {
        // 保存token到localStorage
        localStorage.setItem('token', responseData.access_token);
        console.log('设置token到localStorage');
        
        // 保存用户数据
        const userData = {
          user_id: responseData.user_id,
          username: responseData.username
        };
        localStorage.setItem('userData', JSON.stringify(userData));
        
        // 分发登录action
        const userObj = {
          id: responseData.user_id,
          username: responseData.username,
          email: '',  // API可能需要返回更多用户信息
          avatar: ''
        };
        console.log('分发登录action:', userObj);
        dispatch(loginAction(userObj));
        
        return { success: true };
      } else {
        console.error('登录响应不完整，缺少access_token', responseData);
        throw new Error('登录失败，服务器响应不完整');
      }
    } catch (error: any) {
      console.error('登录失败:', error);
      // 提取更具体的错误信息
      let errorMessage = '用户名或密码错误';
      
      if (error.response) {
        console.error('错误响应:', error.response);
        if (error.response.status === 401) {
          errorMessage = '用户名或密码错误';
        } else if (error.response.status === 503 || error.response.status === 0) {
          errorMessage = '服务器连接失败，请检查网络或稍后再试';
        } else if (error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
      } else if (error.request) {
        console.error('没有收到响应:', error.request);
        errorMessage = '服务器无响应，请检查网络连接';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: any) => {
    try {
      setLoading(true);
      console.log('开始注册流程:', userData);
      
      // 调用API进行注册
      const response: AxiosResponse<UserResponse> = await apiRegister(userData);
      console.log('API返回的注册响应:', response);
      
      // 正确访问response对象中的数据
      const responseData = response.data;
      
      if (responseData && responseData.token) {
        // 保存token到localStorage
        localStorage.setItem('token', responseData.token);
        console.log('设置token到localStorage');
        
        // 保存用户数据
        const userDataToSave = {
          user_id: responseData.user_id,
          username: responseData.username,
          email: responseData.email,
          nickname: responseData.nickname,
          avatar_url: responseData.avatar_url
        };
        localStorage.setItem('userData', JSON.stringify(userDataToSave));
        
        // 分发登录action
        const userObj = {
          id: responseData.user_id,
          username: responseData.username,
          email: responseData.email,
          nickname: responseData.nickname,
          avatar: responseData.avatar_url
        };
        console.log('分发登录action:', userObj);
        dispatch(loginAction(userObj));
        
        return { success: true, user: userObj };
      } else {
        console.error('注册响应缺少token:', responseData);
        throw new Error('注册失败，服务器响应不完整');
      }
    } catch (error: any) {
      console.error('注册失败:', error);
      // 尝试提取更具体的错误信息
      let errorMessage = '注册失败，请稍后重试';
      
      // 改进错误处理，正确提取后端返回的错误信息
      if (error.response && error.response.data) {
        if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      } else if (error.detail) {
        errorMessage = error.detail;
      } else if (error.message) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      }
      
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    console.log('开始登出流程');
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
    dispatch(logoutAction());
    // 可以选择是否强制刷新页面
    // window.location.href = '/';
  };

  const updateProfile = async (formData: FormData) => {
    try {
      setLoading(true);
      // 实际项目中应该调用API
      // const response = await api.put('/users/profile', formData);

      // 这里简单模拟，实际项目中需要实现该API
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 更新用户信息
      const updatedUser = { ...user } as User;
      
      // 从FormData中获取值
      const username = formData.get('username');
      
      if (username) updatedUser.username = username.toString();
      
      // 更新Redux状态
      dispatch(setUser(updatedUser));
      
      return { success: true };
    } catch (error) {
      console.error('更新个人资料失败:', error);
      return { success: false, error: '更新失败，请稍后重试' };
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    isAuthenticated,
    loading: loading || authLoading,
    login,
    register,
    logout,
    checkAuth,
    updateProfile
  };
}; 