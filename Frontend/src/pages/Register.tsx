import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Typography, Divider, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useDispatch } from 'react-redux';
import { startLoading } from '../redux/slices/authSlice';

const { Title, Paragraph } = Typography;

const Register: React.FC = () => {
  const { register, isAuthenticated } = useAuth();
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
    console.log('提交注册表单:', values);
    
    try {
      // 设置全局加载状态
      dispatch(startLoading());
      
      const result = await register(values);
      console.log('注册结果:', result);
      
      if (result.success) {
        message.success('注册成功！');
        // 使用timeout确保状态更新后再跳转
        setTimeout(() => {
          navigate('/');
        }, 300);
      } else {
        message.error(result.error || '注册失败，请稍后重试');
      }
    } catch (error) {
      console.error('注册过程中发生错误:', error);
      message.error('注册过程中发生错误');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-[calc(100vh-64px-70px)]">
      <Card className="w-full max-w-md shadow-lg">
        <div className="text-center mb-6">
          <Title level={2}>创建账号</Title>
          <Paragraph className="text-gray-500">
            加入魔镜Mirror颜值PK平台，开始你的颜值之旅
          </Paragraph>
        </div>

        <Form
          name="register"
          onFinish={onFinish}
          size="large"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入您的用户名！' },
              { min: 3, message: '用户名至少3个字符' }
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入您的邮箱！' },
              { type: 'email', message: '请输入有效的邮箱地址！' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="邮箱" />
          </Form.Item>

          <Form.Item
            name="nickname"
            rules={[
              { required: false, message: '请输入您的昵称！' }
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="昵称（选填）" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入您的密码！' },
              { min: 8, message: '密码至少8个字符' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认您的密码！' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不匹配！'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" className="w-full" loading={loading}>
              注册
            </Button>
          </Form.Item>
        </Form>

        <Divider>或者</Divider>

        <div className="text-center">
          <Paragraph>
            已有账号？
            <Link to="/login" className="text-primary ml-1">
              立即登录
            </Link>
          </Paragraph>
        </div>
      </Card>
    </div>
  );
};

export default Register; 