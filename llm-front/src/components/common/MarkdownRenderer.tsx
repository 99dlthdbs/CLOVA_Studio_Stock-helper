// import "katex/dist/katex.min.css"; // `rehype-katex` does not import the CSS for you
import styled from "@emotion/styled";
import Markdown from "react-markdown";
// import 'highlight.js/styles/a11y-dark.css';
import rehypeHighlight from "rehype-highlight";
// import { Prism as SyntaxHighlighter } from '@fengkx/react-syntax-highlighter';
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import { Suspense } from "react";

interface MarkDownRendererProps {
  text: string;
}

const MarkDownRenderer = ({ text }: MarkDownRendererProps) => {
  return (
    <MarkDownRendererStyle>
      <Suspense>
        <Markdown
          rehypePlugins={[rehypeHighlight, rehypeRaw, rehypeKatex]}
          remarkPlugins={[remarkGfm, remarkMath]}
          children={text}
          components={{
            code({ children, className, ...rest }) {
              // const { className, node, style, ...rest } = props;
              const match = /language-(\w+)/.exec(className || "");

              return match ? (
                <SyntaxHighlighter
                  PreTag="div"
                  children={String(children).replace(/\n$/, "")}
                  language={match[1]}
                  // style={dracula}
                  showLineNumbers={true}
                  wrapLongLines={true}
                >
                  {/*{children}*/}
                </SyntaxHighlighter>
              ) : (
                <InlineCode {...rest} className={className}>
                  {children}
                </InlineCode>
              );
            },
          }}
        />
      </Suspense>
    </MarkDownRendererStyle>
  );
};

export default MarkDownRenderer;

const MarkDownRendererStyle = styled.div`
  display: flex;
  position: relative;
  flex-direction: column;
  //gap: 2rem;

  white-space: break-spaces;

  strong {
    font-weight: bold;
  }
`;

const InlineCode = styled.code`
  padding: 3px 6px;
  border: none;
  border-radius: 0.4rem;
  background-color: var(--highlight01);
  color: var(--text02);
  font-family: "Pretendard", "Malgun Gothic", sans-serif;
`;
