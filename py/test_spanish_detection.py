"""
Test Spanish auto-detection and default inference steps
"""

import re


def test_spanish_detection():
    """Test the Spanish character detection logic"""
    
    # This is the same regex pattern used in tts_service.py
    spanish_chars = re.compile(r'[áéíóúñüÁÉÍÓÚÑÜ¿¡]')
    
    test_cases = [
        {
            'text': 'Hello, this is an English sentence.',
            'expected': False,
            'description': 'English text (no Spanish chars)'
        },
        {
            'text': '¡Hola! ¿Cómo estás?',
            'expected': True,
            'description': 'Spanish text with ¡ and ¿'
        },
        {
            'text': 'El niño está feliz.',
            'expected': True,
            'description': 'Spanish text with ñ'
        },
        {
            'text': 'Está es una oración en español.',
            'expected': True,
            'description': 'Spanish text with á'
        },
        {
            'text': 'This has an accent: café',
            'expected': True,
            'description': 'Mixed text with Spanish chars (é)'
        },
        {
            'text': 'Regular English without special characters',
            'expected': False,
            'description': 'Plain English'
        }
    ]
    
    print('=== Testing Spanish Auto-Detection ===\n')
    print('Test Cases:')
    
    all_passed = True
    for test_case in test_cases:
        detected = bool(spanish_chars.search(test_case['text']))
        passed = detected == test_case['expected']
        all_passed = all_passed and passed
        
        status = '✓' if passed else '✗'
        print(f'\n{status} {test_case["description"]}')
        print(f'  Text: "{test_case["text"]}"')
        print(f'  Expected: {test_case["expected"]}, Detected: {detected}')
    
    return all_passed


def test_default_inference_steps():
    """Test that default inference steps are set correctly"""
    print('\n\n=== Testing Default Inference Steps ===\n')
    
    # Check the source files directly
    checks_passed = []
    
    # Check helper.py
    print('Checking py/helper.py...')
    with open('helper.py', 'r') as f:
        content = f.read()
        if 'steps: int = 15' in content:
            print('✓ helper.py has default steps = 15')
            checks_passed.append(True)
        else:
            print('✗ helper.py does not have default steps = 15')
            checks_passed.append(False)
    
    # Check config.py
    print('\nChecking py/api/src/core/config.py...')
    with open('api/src/core/config.py', 'r') as f:
        content = f.read()
        if 'default_total_steps: int = 15' in content:
            print('✓ config.py has default_total_steps = 15')
            checks_passed.append(True)
        else:
            print('✗ config.py does not have default_total_steps = 15')
            checks_passed.append(False)
    
    # Check JavaScript index.js
    print('\nChecking js/index.js...')
    with open('../js/index.js', 'r') as f:
        content = f.read()
        if 'num_inference_steps || 15' in content:
            print('✓ index.js has default num_inference_steps = 15')
            checks_passed.append(True)
        else:
            print('✗ index.js does not have default num_inference_steps = 15')
            checks_passed.append(False)
    
    return all(checks_passed)


if __name__ == '__main__':
    print('=' * 60)
    print('Running Spanish Auto-Detection and Inference Steps Tests')
    print('=' * 60 + '\n')
    
    test1_passed = test_spanish_detection()
    test2_passed = test_default_inference_steps()
    
    print('\n' + '=' * 60)
    if test1_passed and test2_passed:
        print('✓ All tests passed!')
    else:
        print('✗ Some tests failed')
    print('=' * 60)
