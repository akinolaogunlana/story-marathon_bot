const fs = require('fs').promises;
const path = require('path');
const fetch = require('node-fetch');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_TOKEN = process.env.SUPABASE_TOKEN;

async function fetchSitemapStories() {
  try {
    console.log('🔍 Fetching stories from Supabase sitemaps...');
    
    // Common Supabase Edge Function endpoints for sitemaps/stories
    const endpoints = [
      `${SUPABASE_URL}/functions/v1/sitemap`,
      `${SUPABASE_URL}/functions/v1/stories`,
      `${SUPABASE_URL}/functions/v1/latest-stories`,
      `${SUPABASE_URL}/rest/v1/stories`, // Direct REST API
    ];

    const storiesDir = path.join(__dirname, '../stories');
    await fs.mkdir(storiesDir, { recursive: true });

    const processedStories = new Set();
    
    for (const endpoint of endpoints) {
      try {
        console.log(`📡 Checking ${endpoint}`);
        const response = await fetch(endpoint, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${SUPABASE_TOKEN}`,
            'apikey': SUPABASE_TOKEN,
            'Content-Type': 'application/json',
          },
          timeout: 30000,
        });

        if (response.ok) {
          const data = await response.json();
          
          // Handle different response formats
          const stories = Array.isArray(data) ? data : 
                         data.stories || data.data || data.items || [];
          
          for (const story of stories) {
            const storyId = story.id || story.url || story.title?.slice(0, 50);
            if (storyId && !processedStories.has(storyId)) {
              await saveStory(story, storyId, storiesDir);
              processedStories.add(storyId);
            }
          }
          
          console.log(`✅ Fetched ${stories.length} stories from ${endpoint}`);
        }
      } catch (error) {
        console.log(`⚠️  Skipped ${endpoint}: ${error.message}`);
      }
    }

    console.log(`🎉 Processed ${processedStories.size} unique stories`);
  } catch (error) {
    console.error('💥 Failed to fetch stories:', error);
    process.exit(1);
  }
}

async function saveStory(story, storyId, storiesDir) {
  const storyFile = path.join(storiesDir, `${storyId.replace(/[^a-z0-9]/gi, '_')}.json`);
  const storyData = {
    id: story.id,
    title: story.title || story.name,
    url: story.url || story.link,
    content: story.content || story.excerpt,
    published: story.published_at || story.created_at || new Date().toISOString(),
    source: story.source || 'supabase',
    raw: story,
  };

  await fs.writeFile(storyFile, JSON.stringify(storyData, null, 2));
}

fetchSitemapStories();
