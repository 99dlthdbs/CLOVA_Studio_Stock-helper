import { css, Global } from "@emotion/react";

const style = css`
  * {
    margin: 0;
    padding: 0;

    box-sizing: border-box;
    font-family:
      "Pretendard Variable",
      Pretendard,
      -apple-system,
      BlinkMacSystemFont,
      system-ui,
      Roboto,
      "Helvetica Neue",
      "Segoe UI",
      "Apple SD Gothic Neo",
      "Noto Sans KR",
      "Malgun Gothic",
      "Apple Color Emoji",
      "Segoe UI Emoji",
      "Segoe UI Symbol",
      sans-serif;

    --theme-color-1: #352f44;
    --theme-color-2: #7a6f94;
    --theme-color-3: #b9b4c7;
    --theme-color-4: #faf0e6;

    --highlight-1: #a899ccff;

    --bg-1: #2a2538;
    --bg-2: #241f32;
    --bg-3: #1e1a2d;
    --bg-4: #181422;

    font-weight: 400;
  }

  #root {
    margin: 0;
    padding: 0;

    width: 100%;
    min-height: 100vh;
  }

  a {
    text-decoration: none;
    color: inherit;

    &:focus,
    &:hover {
      color: inherit;
    }
  }

  button {
    padding: 0;

    background-color: inherit;

    cursor: pointer;
    border: none;

    &:focus {
      outline: none;
    }
  }

  ul,
  li {
    list-style: none;
  }

  input,
  textarea {
    background-color: inherit;

    &:focus {
      outline: none;
    }
  }
`;

const GlobalStyle = () => {
  return <Global styles={style} />;
};

export default GlobalStyle;
