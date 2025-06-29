import React from 'react';
import { Layout } from 'antd';

const { Footer: AntFooter } = Layout;

const Footer: React.FC = () => {
  return (
    <AntFooter className="text-center bg-white mt-6">
      <div className="py-4">
        <p className="mb-2">魔镜Mirror颜值PK平台 ©{new Date().getFullYear()}</p>
        <p className="text-gray-500 text-sm">
          基于人脸识别技术的娱乐社交Web应用
        </p>
      </div>
    </AntFooter>
  );
};

export default Footer; 