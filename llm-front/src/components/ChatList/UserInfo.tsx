import styled from "@emotion/styled";
import UserIcon from "@/assets/icon-user.svg?react";

interface UserInfoProps {
  name: string;
}

const UserInfo = ({ name }: UserInfoProps) => {
  return (
    <UserInfoContainer>
      <IconContainer>
        <UserIcon
          width={"1.25rem"}
          height={"1.25rem"}
          color={"var(--theme-color-4)"}
        />
      </IconContainer>
      <Text>{name}</Text>
    </UserInfoContainer>
  );
};

export default UserInfo;

const UserInfoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;

  padding: 1rem;
`;

const IconContainer = styled.div``;

const Text = styled.p`
  font-size: 1rem;
`;
