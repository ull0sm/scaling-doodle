-- Add UPDATE and DELETE policies for chat_sessions

create policy "Users can update their own sessions" on chat_sessions
  for update using (auth.uid() = user_id);

create policy "Users can delete their own sessions" on chat_sessions
  for delete using (auth.uid() = user_id);

-- Ensure chat_messages can be deleted if needed (though ON DELETE CASCADE on the foreign key usually handles this)
create policy "Users can delete messages from their sessions" on chat_messages
  for delete using (
    exists (
      select 1 from chat_sessions
      where chat_sessions.id = chat_messages.session_id
      and chat_sessions.user_id = auth.uid()
    )
  );
