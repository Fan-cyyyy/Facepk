import React, { useState, useEffect } from 'react';
import { Menu, Dropdown, Avatar, Button, Space } from 'antd';
import { UserOutlined, LogoutOutlined, SettingOutlined, DownOutlined } from '@ant-design/icons';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const Header: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [current, setCurrent] = useState('/');

  // 根据路由变化更新当前选中的菜单项
  useEffect(() => {
    setCurrent(location.pathname);
  }, [location.pathname]);

  // 调试日志
  useEffect(() => {
    console.log('Header认证状态:', { isAuthenticated, user });
  }, [isAuthenticated, user]);

  const handleMenuClick = (e: any) => {
    setCurrent(e.key);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const menuItems = [
    {
      key: '/',
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/rankings',
      label: <Link to="/rankings">排行榜</Link>,
    },
    {
      key: '/scoring',
      label: <Link to="/scoring">颜值评分</Link>,
    },
    {
      key: '/battle',
      label: <Link to="/battle">颜值对战</Link>,
    },
  ];

  const dropdownMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        <Link to="/profile">个人中心</Link>
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        <Link to="/settings">账号设置</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        退出登录
      </Menu.Item>
    </Menu>
  );

  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center">
          <Link to="/" className="text-xl font-bold text-primary mr-8">
            魔镜Mirror
          </Link>
          <Menu
            mode="horizontal"
            selectedKeys={[current]}
            onClick={handleMenuClick}
            className="border-0"
            items={menuItems}
          />
        </div>
        
        <div>
          {isAuthenticated && user ? (
            <Dropdown overlay={dropdownMenu} trigger={['click']}>
              <Space className="cursor-pointer">
                <Avatar 
                  src={user.avatar} 
                  icon={!user.avatar && <UserOutlined />}
                />
                <span>{user.username}</span>
                <DownOutlined />
              </Space>
            </Dropdown>
          ) : (
            <Space>
              <Button type="text" onClick={() => navigate('/login')}>
                登录
              </Button>
              <Button type="primary" onClick={() => navigate('/register')}>
                注册
              </Button>
            </Space>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 