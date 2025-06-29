import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Upload, Avatar, Card, Tabs, Row, Col, Typography, Statistic, message } from 'antd';
import { UserOutlined, UploadOutlined, CameraOutlined, TrophyOutlined, StarOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { useSelector } from 'react-redux';
import { RootState } from '../redux/store';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

const Profile: React.FC = () => {
  const { user, updateProfile } = useAuth();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [avatar, setAvatar] = useState<string | null>(null);
  const userScores = useSelector((state: RootState) => state.score.userScores);

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        bio: user.bio || '',
      });
      setAvatar(user.avatar);
    }
  }, [user, form]);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const formData = new FormData();
      Object.keys(values).forEach(key => {
        if (values[key] !== undefined && key !== 'avatar') {
          formData.append(key, values[key]);
        }
      });

      if (values.avatar && values.avatar.file) {
        formData.append('avatar', values.avatar.file);
      }

      const result = await updateProfile(formData);
      if (result.success) {
        message.success('个人资料更新成功');
      } else {
        message.error(result.error || '更新失败，请稍后重试');
      }
    } catch (error) {
      message.error('更新过程中发生错误');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarChange = (info: any) => {
    if (info.file.status === 'done') {
      setAvatar(URL.createObjectURL(info.file.originFileObj));
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <Row gutter={24}>
        <Col xs={24} md={8}>
          <Card className="mb-6 shadow-md">
            <div className="text-center mb-4">
              <div className="relative inline-block">
                <Avatar 
                  size={120} 
                  src={avatar} 
                  icon={<UserOutlined />} 
                  className="mb-4"
                />
                <Upload 
                  name="avatar"
                  showUploadList={false}
                  customRequest={({ file, onSuccess }: any) => {
                    setTimeout(() => {
                      onSuccess("ok");
                    }, 0);
                  }}
                  onChange={handleAvatarChange}
                >
                  <Button 
                    type="primary" 
                    shape="circle" 
                    icon={<CameraOutlined />} 
                    size="small"
                    className="absolute bottom-4 right-0"
                  />
                </Upload>
              </div>
              <Title level={3}>{user?.username}</Title>
              <Paragraph className="text-gray-500">{user?.email}</Paragraph>
            </div>

            <Row className="text-center">
              <Col span={12}>
                <Statistic 
                  title="参与评分" 
                  value={userScores?.rated || 0} 
                  prefix={<StarOutlined />} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="获得评分" 
                  value={userScores?.received || 0} 
                  prefix={<TrophyOutlined />} 
                />
              </Col>
            </Row>
          </Card>

          <Card className="shadow-md">
            <Title level={4}>我的统计</Title>
            <Row gutter={[16, 16]} className="mt-4">
              <Col span={12}>
                <Statistic title="平均得分" value={userScores?.averageScore || 0} suffix="分" precision={1} />
              </Col>
              <Col span={12}>
                <Statistic title="PK胜率" value={userScores?.winRate || 0} suffix="%" precision={1} />
              </Col>
              <Col span={12}>
                <Statistic title="参与PK" value={userScores?.battles || 0} />
              </Col>
              <Col span={12}>
                <Statistic title="排名" value={userScores?.ranking || '-'} />
              </Col>
            </Row>
          </Card>
        </Col>

        <Col xs={24} md={16}>
          <Card className="shadow-md">
            <Tabs defaultActiveKey="profile">
              <TabPane tab="个人资料" key="profile">
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={onFinish}
                  initialValues={{ remember: true }}
                >
                  <Form.Item
                    name="username"
                    label="用户名"
                    rules={[{ required: true, message: '请输入用户名！' }]}
                  >
                    <Input prefix={<UserOutlined />} placeholder="用户名" />
                  </Form.Item>

                  <Form.Item
                    name="email"
                    label="邮箱"
                    rules={[
                      { required: true, message: '请输入邮箱！' },
                      { type: 'email', message: '请输入有效的邮箱地址！' }
                    ]}
                  >
                    <Input disabled />
                  </Form.Item>

                  <Form.Item
                    name="bio"
                    label="个人简介"
                  >
                    <Input.TextArea rows={4} placeholder="介绍一下自己..." />
                  </Form.Item>

                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                      保存修改
                    </Button>
                  </Form.Item>
                </Form>
              </TabPane>
              
              <TabPane tab="安全设置" key="security">
                <Form layout="vertical">
                  <Form.Item
                    name="currentPassword"
                    label="当前密码"
                    rules={[{ required: true, message: '请输入当前密码！' }]}
                  >
                    <Input.Password placeholder="当前密码" />
                  </Form.Item>

                  <Form.Item
                    name="newPassword"
                    label="新密码"
                    rules={[
                      { required: true, message: '请输入新密码！' },
                      { min: 6, message: '密码至少6个字符' }
                    ]}
                  >
                    <Input.Password placeholder="新密码" />
                  </Form.Item>

                  <Form.Item
                    name="confirmPassword"
                    label="确认新密码"
                    dependencies={['newPassword']}
                    rules={[
                      { required: true, message: '请确认新密码！' },
                      ({ getFieldValue }) => ({
                        validator(_, value) {
                          if (!value || getFieldValue('newPassword') === value) {
                            return Promise.resolve();
                          }
                          return Promise.reject(new Error('两次输入的密码不一致！'));
                        },
                      }),
                    ]}
                  >
                    <Input.Password placeholder="确认新密码" />
                  </Form.Item>

                  <Form.Item>
                    <Button type="primary" htmlType="submit">
                      修改密码
                    </Button>
                  </Form.Item>
                </Form>
              </TabPane>
            </Tabs>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Profile; 