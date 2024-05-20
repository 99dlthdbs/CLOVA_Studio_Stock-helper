import AppRouter from "@/AppRouter";
import GlobalStyle from "@/css/GlobalStyle";
import { initialAxios } from "@/apis";

function App() {
  initialAxios();

  return (
    <>
      <GlobalStyle />
      <AppRouter />
    </>
  );
}

export default App;
