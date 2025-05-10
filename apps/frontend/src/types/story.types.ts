interface PlayerCharacter {
  name: string;
  image_dir: string;
}

export interface Story {
  user_id: number;
  title: string;
  description: string;
  brief_description: string;
  rules: string[];
  uuid: string;
  player_character: PlayerCharacter;
}
