import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Header from "./components/common/Header";
import Footer from "./components/common/Footer";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import Scoring from "./pages/Scoring";
import Battle from "./pages/Battle";
import Rankings from "./pages/Rankings";
import { Spin } from 'antd';

// 私有路由组件
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();
  
  // 添加调试日志
  console.log('PrivateRoute检查认证状态:', { isAuthenticated, loading });
  
  // 如果正在加载，显示加载指示器
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }
  
  // 如果未认证，重定向到登录页面
  if (!isAuthenticated) {
    console.log('未认证，重定向到登录页面');
    return <Navigate to="/login" replace />;
  }
  
  // 已认证，渲染子组件
  console.log('已认证，渲染受保护的组件');
  return <>{children}</>;
};

const App: React.FC = () => {
  const { checkAuth, isAuthenticated, loading } = useAuth();
  const [appReady, setAppReady] = useState(false);
  
  // 初始化应用时检查认证状态
  useEffect(() => {
    const initApp = async () => {
      console.log('初始化应用，检查认证状态');
      await checkAuth();
      console.log('认证状态检查完成:', { isAuthenticated, loading });
      setAppReady(true);
    };
    
    initApp();
  }, [checkAuth]);
  
  // 如果应用尚未准备好，显示加载指示器
  if (!appReady) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spin size="large" tip="加载应用..." />
      </div>
    );
  }
  
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={
            <PrivateRoute>
              <Profile />
            </PrivateRoute>
          } />
          <Route path="/scoring" element={
            <PrivateRoute>
              <Scoring />
            </PrivateRoute>
          } />
          <Route path="/battle" element={
            <PrivateRoute>
              <Battle />
            </PrivateRoute>
          } />
          <Route path="/rankings" element={<Rankings />} />
          {/* 其他页面将在后续开发中添加 */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
};

export default App; 