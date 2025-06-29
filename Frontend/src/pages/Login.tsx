import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Typography, Divider, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useDispatch } from 'react-redux';
import { startLoading } from '../redux/slices/authSlice';

const { Title, Paragraph } = Typography;

const Login: React.FC = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  // 如果已经登录，直接跳转到首页
  useEffect(() => {
    if (isAuthenticated) {
      console.log('用户已登录，跳转到首页');
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const onFinish = async (values: any) => {
    setLoading(true);
    console.log('提交登录表单:', values);
    
    try {
      // 设置全局加载状态
      dispatch(startLoading());
      
      const result = await login(values);
      console.log('登录结果:', result);
      
      if (result.success) {
        message.success('登录成功！');
        // 使用timeout确保状态更新后再跳转
        setTimeout(() => {
          navigate('/');
        }, 300);
      } else {
        message.error(result.error || '登录失败，请检查用户名和密码');
      }
    } catch (error) {
      console.error('登录过程中发生错误:', error);
      message.error('登录过程中发生错误');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-[calc(100vh-64px-70px)]">
      <Card className="w-full max-w-md shadow-lg">
        <div className="text-center mb-6">
          <Title level={2}>欢迎回来</Title>
          <Paragraph className="text-gray-500">
            登录魔镜Mirror颜值PK平台，开始你的颜值之旅
          </Paragraph>
        </div>

        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          size="large"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入您的用户名！' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入您的密码！' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" className="w-full" loading={loading}>
              登录
            </Button>
          </Form.Item>

          <div className="text-center">
            <Link to="/forgot-password" className="text-primary">
              忘记密码？
            </Link>
          </div>
        </Form>

        <Divider>或者</Divider>

        <div className="text-center">
          <Paragraph>
            还没有账号？
            <Link to="/register" className="text-primary ml-1">
              立即注册
            </Link>
          </Paragraph>
        </div>
      </Card>
    </div>
  );
};

export default Login; 