import styled from "@emotion/styled";
import Lottie from "react-lottie";
import loadingData from "@/assets/loading-animation.json";

interface MessageProps {
  role: string;
  content: string;
}

const Message = ({ role, content }: MessageProps) => {
  const defaultOptions = {
    loop: true,
    autoplay: true,
    animationData: loadingData,
    rendererSettings: {
      preserveAspectRatio: "xMidYMid slice",
    },
  };

  return (
    <MessageContainer>
      <RoleContainer>
        <RoleText>{role === "user" ? "You" : "Stockelper"}</RoleText>
      </RoleContainer>
      <ContentContainer>
        <ContentText>
          {content ? (
            content
          ) : (
            <IconConatainer>
              <Lottie
                options={defaultOptions}
                width={"1.75rem"}
                height={"1.75rem"}
                speed={1.25}
              />
            </IconConatainer>
          )}
        </ContentText>
      </ContentContainer>
    </MessageContainer>
  );
};

export default Message;

const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  padding: 1rem;
`;

const RoleContainer = styled.div``;

const RoleText = styled.p`
  font-weight: 600;
`;

const ContentContainer = styled.div``;

const IconConatainer = styled.div`
  width: fit-content;
  height: fit-content;
`;

const ContentText = styled.div`
  line-height: 1.8rem;
`;
