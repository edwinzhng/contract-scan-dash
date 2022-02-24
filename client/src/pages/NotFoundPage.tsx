import React from "react";
import styled from "styled-components";

const NotFoundPageWrapper = styled.div`
  width: 100%;
  margin: 120px auto;
  text-align: center;
  font-size: 24px;
  color: #fff;
`;

const NotFoundPage = () => {
  return <NotFoundPageWrapper>Page not found</NotFoundPageWrapper>;
};

export default NotFoundPage;
