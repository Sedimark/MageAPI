import random

class NameGenerator:
    adjectives = [
        # Emotions/Mood
        'happy', 'angry', 'sleepy', 'crazy', 'lazy', 'excited', 'grumpy',
        'cheerful', 'gloomy', 'peaceful', 'nervous', 'calm', 'energetic',
        'relaxed', 'stressed', 'confident', 'shy', 'brave', 'scared',
        
        # Actions
        'dancing', 'jumping', 'flying', 'running', 'singing', 'sleeping',
        'crawling', 'swimming', 'bouncing', 'skating', 'skipping', 'diving',
        'rolling', 'spinning', 'floating', 'dashing', 'prancing', 'marching',
        
        # Characteristics
        'tiny', 'giant', 'mighty', 'magical', 'mysterious', 'clever', 'silly',
        'witty', 'clumsy', 'graceful', 'fierce', 'gentle', 'wild', 'tame',
        'loud', 'quiet', 'bright', 'dark', 'sneaky', 'bold', 'shy',
        
        # Qualities
        'sparkly', 'glowing', 'shiny', 'dull', 'fuzzy', 'fluffy', 'smooth',
        'rough', 'sharp', 'bubbly', 'squishy', 'solid', 'liquid', 'gaseous',
        'transparent', 'opaque', 'dense', 'light', 'heavy', 'soft'
    ]
    
    nouns = [
        # Animals
        'banana', 'apple', 'penguin', 'cat', 'dragon', 'potato', 'pizza',
        'monkey', 'panda', 'dolphin', 'unicorn', 'cookie', 'elephant', 'lion',
        'tiger', 'bear', 'wolf', 'fox', 'rabbit', 'deer', 'moose', 'eagle',
        'hawk', 'owl', 'parrot', 'flamingo', 'whale', 'shark', 'octopus',
        'squid', 'butterfly', 'bee', 'ant', 'spider', 'giraffe', 'zebra',
        'kangaroo', 'koala', 'sloth', 'raccoon', 'squirrel', 'hedgehog',
        
        # Foods
        'pizza', 'burger', 'taco', 'sushi', 'pasta', 'cookie', 'cake',
        'donut', 'sandwich', 'pancake', 'waffle', 'muffin', 'bagel', 'bread',
        'cheese', 'chocolate', 'candy', 'ice_cream', 'smoothie', 'milkshake',
        
        # Objects
        'robot', 'rocket', 'star', 'moon', 'sun', 'cloud', 'rainbow',
        'diamond', 'crystal', 'book', 'pencil', 'phone', 'computer', 'guitar',
        'drum', 'piano', 'camera', 'clock', 'lamp', 'chair', 'table',
        
        # Nature
        'tree', 'flower', 'mountain', 'river', 'ocean', 'forest', 'desert',
        'island', 'volcano', 'glacier', 'canyon', 'waterfall', 'beach',
        'garden', 'meadow', 'valley', 'hill', 'cave', 'reef', 'oasis'
    ]
    
    colors = [
        # Basic Colors
        'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink',
        'brown', 'black', 'white', 'gray', 'golden', 'silver',
        
        # Light Variations
        'light_blue', 'light_green', 'light_pink', 'light_purple',
        'pale_yellow', 'cream', 'ivory', 'beige',
        
        # Dark Variations
        'dark_blue', 'dark_green', 'dark_red', 'dark_purple', 'navy',
        'maroon', 'forest_green', 'midnight_blue',
        
        # Mixed Colors
        'turquoise', 'teal', 'magenta', 'violet', 'indigo', 'cyan',
        'burgundy', 'crimson', 'azure', 'coral', 'salmon',
        
        # Metallic Colors
        'bronze', 'copper', 'platinum', 'rose_gold', 'metallic_blue',
        'chrome', 'titanium',
        
        # Special Colors
        'rainbow', 'iridescent', 'neon', 'pastel', 'translucent',
        'holographic', 'prismatic', 'pearlescent'
    ]
    
    @classmethod
    def generate(cls, include_color=False):
        adj = random.choice(cls.adjectives)
        noun = random.choice(cls.nouns)
        
        if include_color:
            color = random.choice(cls.colors)
            return f"{adj}_{color}_{noun}"
        return f"{adj}_{noun}"
