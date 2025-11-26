-- Create chat_sessions table
create table if not exists chat_sessions (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users not null,
  title text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create chat_messages table
create table if not exists chat_messages (
  id uuid default gen_random_uuid() primary key,
  session_id uuid references chat_sessions on delete cascade not null,
  role text not null,
  content text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS)
alter table chat_sessions enable row level security;
alter table chat_messages enable row level security;

-- Policies for chat_sessions
create policy "Users can select their own sessions" on chat_sessions
  for select using (auth.uid() = user_id);

create policy "Users can insert their own sessions" on chat_sessions
  for insert with check (auth.uid() = user_id);

-- Policies for chat_messages
create policy "Users can select messages from their sessions" on chat_messages
  for select using (
    exists (
      select 1 from chat_sessions
      where chat_sessions.id = chat_messages.session_id
      and chat_sessions.user_id = auth.uid()
    )
  );

create policy "Users can insert messages to their sessions" on chat_messages
  for insert with check (
    exists (
      select 1 from chat_sessions
      where chat_sessions.id = chat_messages.session_id
      and chat_sessions.user_id = auth.uid()
    )
  );
