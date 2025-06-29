import axios, { AxiosResponse } from 'axios';

// 获取API基础URL
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 增加超时时间到30秒
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(`请求: ${config.method?.toUpperCase()} ${config.url}`, config);
    return config;
  },
  error => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`响应: ${response.config.url}`, response.data);
    return response; // 返回整个response对象，而不仅仅是data部分
  },
  error => {
    console.error('API错误:', error);
    
    if (error.response) {
      // 请求已发出，但服务器响应状态码不在 2xx 范围内
      console.error('响应状态:', error.response.status);
      console.error('响应数据:', error.response.data);
      
      if (error.response.status === 401) {
        // 未授权，可能是token过期
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(error.response.data);
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('请求已发出但无响应:', error.request);
      return Promise.reject({ error: '服务器无响应，请检查网络连接' });
    } else {
      // 请求配置有问题
      console.error('请求错误:', error.message);
      return Promise.reject({ error: '请求错误: ' + error.message });
    }
  }
);

// 认证响应接口
export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
}

export interface UserResponse {
  user_id: number;
  username: string;
  email: string;
  nickname?: string;
  avatar_url?: string;
  token?: string;
  token_type?: string;
}

// 评分结果接口
export interface ScoreDetail {
  category: string;
  score: number;
  description: string;
}

export interface ScoreResponse {
  success: boolean;
  error?: string;
  score_id?: number;
  face_score?: number;
  image_url?: string;
  feature_highlights?: any;
  score_details?: ScoreDetail[];
  created_at?: string;
  is_public?: boolean;
}

// 对战用户信息
export interface MatchUser {
  user_id: number;
  username: string;
  avatar_url?: string;
  score: number;
  image_url: string;
}

// 对战结果
export interface MatchResponse {
  success: boolean;
  error?: string;
  match_id?: number;
  challenger?: MatchUser;
  opponent?: MatchUser;
  result?: string; // "Win", "Lose", "Tie"
  points_change?: number;
  new_rating?: number;
  matched_at?: string;
}

/**
 * 上传照片并获取颜值评分
 * @param imageFile 图片文件
 * @param isPublic 是否公开
 * @returns 评分结果
 */
export const uploadAndScore = async (imageFile: File, isPublic: boolean = true): Promise<ScoreResponse> => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('is_public', isPublic.toString());
  
  try {
    const response = await api.post('/scores', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    return response.data;
  } catch (error: any) {
    console.error('上传照片并评分失败:', error);
    return {
      success: false,
      error: error.message || '上传照片并评分失败'
    };
  }
};

/**
 * 获取用户评分历史
 * @param userId 用户ID，不传则获取当前用户的
 * @param page 页码
 * @param limit 每页条数
 * @returns 评分历史分页数据
 */
export const getUserScores = async (
  userId?: number, 
  page: number = 1, 
  limit: number = 10
) => {
  const params: any = { page, limit };
  if (userId) {
    params.user_id = userId;
  }
  
  return api.get('/scores', { params });
};

/**
 * 获取全球排行榜数据
 * @param page 页码
 * @param limit 每页条数
 * @returns 排行榜数据
 */
export const getGlobalRankings = async (page: number = 1, limit: number = 10) => {
  // 添加时间戳参数，避免缓存
  const timestamp = new Date().getTime();
  return api.get('/rankings/global', {
    params: { page, limit, t: timestamp }
  });
};

/**
 * 获取单条评分详情
 * @param scoreId 评分ID
 * @returns 评分详情
 */
export const getScoreDetail = async (scoreId: number) => {
  return api.get(`/scores/${scoreId}`);
};

/**
 * 用户登录
 * @param username 用户名
 * @param password 密码
 * @returns 登录结果，包含token
 */
export const login = async (username: string, password: string): Promise<AxiosResponse<TokenResponse>> => {
  console.log('开始登录请求，用户名:', username);
  
  // 使用URLSearchParams代替FormData，因为OAuth2要求x-www-form-urlencoded格式
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  
  try {
    const response = await api.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
    });
    console.log('登录响应:', response);
    return response;
  } catch (error: any) {
    console.error('登录失败:', error);
    if (error.response) {
      console.error('错误状态码:', error.response.status);
      console.error('错误详情:', error.response.data);
    }
    throw error;
  }
};

/**
 * 用户注册
 * @param userData 用户数据
 * @returns 注册结果，包含token
 */
export const register = async (userData: any): Promise<AxiosResponse<UserResponse>> => {
  // 删除确认密码字段，后端不需要
  const { confirmPassword, ...userDataToSend } = userData;
  
  // 确保nickname字段存在，如果没有则使用username
  if (!userDataToSend.nickname) {
    userDataToSend.nickname = userDataToSend.username;
  }
  
  console.log('注册请求数据:', JSON.stringify(userDataToSend));
  
  try {
    // 由于响应拦截器已经提取了data部分，直接返回
    const response = await api.post('/auth/register', userDataToSend);
    console.log('注册成功，服务器响应:', response);
    return response;
  } catch (error: any) {
    console.error('注册请求失败:', error);
    // 如果有详细的错误信息，打印出来
    if (error.response) {
      console.error('错误状态码:', error.response.status);
      console.error('错误详情:', error.response.data);
    }
    throw error;
  }
};

/**
 * 获取用户对战历史
 * @param userId 用户ID
 * @param page 页码
 * @param limit 每页条数
 * @param result 过滤结果类型
 * @returns 对战历史
 */
export const getUserMatches = async (userId: number, page: number = 1, limit: number = 10, result?: string) => {
  const params: any = { page, limit };
  if (result) {
    params.result = result;
  }
  
  return api.get(`/matches/user/${userId}`, { params });
};

/**
 * 发起PK对战
 * @param opponentId 对手ID
 * @param scoreId 自己的评分ID
 * @returns 对战结果
 */
export const createMatch = async (opponentId: number, scoreId: number): Promise<MatchResponse> => {
  try {
    const response = await api.post('/matches', {
      opponent_id: opponentId,
      score_id: scoreId
    });
    return response.data;
  } catch (error: any) {
    console.error('创建PK对战失败:', error);
    return {
      success: false,
      error: error.message || '创建PK对战失败'
    };
  }
};

/**
 * 获取对战详情
 * @param matchId 对战ID
 * @returns 对战详情
 */
export const getMatchDetail = async (matchId: number): Promise<MatchResponse> => {
  try {
    const response = await api.get(`/matches/${matchId}`);
    return response.data;
  } catch (error: any) {
    console.error('获取对战详情失败:', error);
    return {
      success: false,
      error: error.message || '获取对战详情失败'
    };
  }
};

export default api; 