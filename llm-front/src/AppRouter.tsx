import { Route, Routes } from "react-router-dom";
import Main from "@/pages";
import Chat from "@/pages/chat";
import ChatLayout from "@/pages/chat/_layout";
import Login from "@/pages/login";
import Signup from "@/pages/signup";
import Layout from "@/pages/_laout";

const AppRouter = () => {
  return (
    <>
      <Routes>
        <Route element={<Layout />}>
          <Route path={"/"} element={<Main />} />
        </Route>

        <Route path={"/login"} element={<Login />} />
        <Route path={"/signup"} element={<Signup />} />

        <Route element={<ChatLayout />}>
          <Route path={"/chat"} element={<Chat />} />
          <Route path={"/chat/:id"} element={<Chat />} />
        </Route>
      </Routes>
    </>
  );
};

export default AppRouter;
