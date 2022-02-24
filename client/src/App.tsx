import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import DiffPage from "./pages/DiffPage";
import NotFoundPage from "./pages/NotFoundPage";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<NotFoundPage />} />
        <Route path="/diff" element={<DiffPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
