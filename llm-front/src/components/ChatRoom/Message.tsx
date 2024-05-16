import styled from "@emotion/styled";

interface MessageProps {
  role: string;
  content: string;
}

const Message = ({ role, content }: MessageProps) => {
  return (
    <MessageContainer>
      <RoleContainer>
        <RoleText>{role === "user" ? "You" : "Stockelper"}</RoleText>
      </RoleContainer>
      <ContentContainer>
        <ContentText>{content}</ContentText>
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

const ContentText = styled.p`
  line-height: 1.8rem;
`;
