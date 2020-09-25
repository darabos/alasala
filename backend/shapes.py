cube = {'size': [1, 1, 1], 'color': '#fff'}

chicken = dict(
    size=[1, 1, 0.9],
    color='#eee',
    children=[
      dict(size=[0.2, 0.2, 0.2], dir='front', color='#dd3'),
      dict(size=[0.2, 0.6, 0.4], dir='up', color='#900'),
      dict(size=[0.7, 0.7, 0.2], dir='left'),
      dict(size=[0.7, 0.7, 0.2], dir='right'),
      ])

bull = dict(
    size=[1, 1, 1.8],
    color='#333',
    children=[
      dict(size=[1, 0.2, 0.2], dir='front', offset=[0, 0, 0.5]),
      dict(size=[0.2, 0.2, 0.2], dir='front', offset=[0.3, 0, 0.3], color='#990'),
      dict(size=[0.2, 0.2, 0.2], dir='front', offset=[-0.3, 0, 0.3], color='#990'),
      dict(size=[0.5, 0.3, 0.3], dir='left', offset=[0, 0, 0.8], color='#999'),
      dict(size=[0.5, 0.3, 0.3], dir='right', offset=[0, 0, 0.8], color='#999'),
      dict(size=[0.3, 0.6, 0.6], dir='left'),
      dict(size=[0.3, 0.6, 0.6], dir='right'),
      ])

ghost = dict(
    size=[1, 1, 0.8],
    color='#339',
    children=[
      dict(size=[0.1, 0.1, 0.1], dir='front', offset=[0.2, 0, 0], color='#fff'),
      dict(size=[0.1, 0.1, 0.1], dir='front', offset=[-0.2, 0, 0], color='#fff'),
      dict(size=[0.3, 0.3, 0.2], dir='up', children=[
        dict(size=[0.1, 0.1, 0.2], dir='up', children=[
          dict(size=[0.3, 0.3, 0.3], dir='up', color='#fff', mass=0.001)
        ])
      ])
    ])

rats = dict(
      size=[0.2, 0.3, 0.2],
      color='#665',
      children=[
        dict(size=[0.1, 0.3, 0.1], dir='back', color='#333'),
        dict(size=[0.1, 0.1, 0.1], dir='front'),
  dict(
    dir='left',
    offset=[0.6, 0.2, 0],
      size=[0.2, 0.3, 0.2],
      color='#665',
      children=[
        dict(size=[0.1, 0.3, 0.1], dir='back', color='#333'),
        dict(size=[0.1, 0.1, 0.1], dir='front'),
      ]),
  dict(
    dir='right',
    offset=[-0.6, 0.3, 0],
      size=[0.2, 0.3, 0.2],
      color='#665',
      children=[
        dict(size=[0.1, 0.3, 0.1], dir='back', color='#333'),
        dict(size=[0.1, 0.1, 0.1], dir='front'),
      ])
      ])

knight = dict(
    size=[0.9, 0.9, 0.9],
    color='#888',
    children=[
      dict(size=[0.5, 0.5, 0.6], dir='up', children=[
        dict(size=[0.1, 0.1, 0.6], dir='up', color='#900')]),
      dict(size=[0.5, 0.5, 0.5], dir='left', offset=[0, -0.2, 0.4], children=[
        dict(size=[0.8, 0.1, 0.8], dir='front', color='#03d')]),
      dict(size=[0.5, 0.5, 0.5], dir='right', offset=[0, 0, 0.4], children=[
        dict(size=[0.1, 1, 0.1], dir='down', offset=[0, -0.5, 0], color='#fff')]),
      ])

wizard = dict(
    size=[0.8, 0.8, 0.7],
    color='#728',
    children=[
      # Staff.
      dict(size=[0.1, 0.1, 1.6], dir='right', offset=[-0.4, 0, 0.45], color='#874'),
      # Hat.
      dict(size=[1.2, 1.2, 0.1], dir='up', children=[
      dict(size=[0.8, 0.8, 0.1], dir='up', children=[
      dict(size=[0.4, 0.4, 0.1], dir='up', color='#ca3', children=[
      dict(size=[0.2, 0.2, 0.2], dir='up', color='#728', children=[
      dict(size=[0.1, 0.1, 0.2], dir='up')])])])]),
    ])

steelking = dict(
    size=[1, 1, 1],
    color='#aaa',
    children=[
      dict(size=[1, 1, 0.1], dir='up', color='#336', children=[
        dict(size=[0.1, 0.1, 0.6], dir='up', offset=[-0.4, -0.4, 0]),
        dict(size=[0.1, 0.1, 0.6], dir='up', offset=[-0.4, 0.4, 0]),
        dict(size=[0.1, 0.1, 0.6], dir='up', offset=[0.4, -0.4, 0]),
        dict(size=[0.1, 0.1, 0.6], dir='up', offset=[0.4, 0.4, 0]),
      ]),
      dict(size=[0.1, 0.1, 0.4], dir='right', color='#336', children=[
        dict(size=[0.1, 0.2, 0.1], dir='back', mass=0.0001),
        dict(size=[0.1, 0.7, 0.1], dir='front', mass=0.0001),
      ])
    ])

scientist = dict(
    size=[0.9, 0.8, 1],
    color='#765',
    children=[
      dict(size=[1, 1, 0.1], dir='up', color='#432', children=[
        dict(size=[0.6, 0.6, 0.6], dir='up')]),
      dict(size=[0.4, 0.1, 0.4], dir='front', offset=[0.3, -0.1, 0.2], color='#fff'),
      dict(size=[0.4, 0.1, 0.4], dir='front', offset=[-0.3, -0.1, 0.2], color='#fff'),
    ])

monkey = dict(
    size=[0.2, 0.2, 0.5],
    mass=1,
    color='#987',
    children=[
      dict(size=[0.6, 0.5, 0.7], dir='up', offset=[0.3, 0, 0], children=[
        dict(size=[0.2, 0.2, 0.5], dir='down', offset=[0.3, 0, 0]),
        dict(size=[0.5, 0.2, 0.2], dir='left', offset=[0, 0, 0.2]),
        dict(size=[0.5, 0.2, 0.2], dir='right', offset=[0, 0, 0.2]),
      ]),
    ])

healer = {
    'size': [1, 1, 1.5],
    'color': '#961',
    'children': [
      { 'size': [0.3, 0.2, 0.3], 'dir': 'front' },
      { 'size': [0.3, 0.2, 0.4], 'offset': [0.3, 0, 0], 'dir': 'up' },
      { 'size': [0.3, 0.2, 0.4], 'offset': [-0.3, 0, 0], 'dir': 'up' },
      {
        'size': [0.5, 0.2, 0.2],
        'dir': 'left',
        'children': [{ 'size': [0.4, 0.2, 0.2], 'dir': 'left' }],
      },
      {
        'size': [0.5, 0.2, 0.2],
        'dir': 'right',
        'children': [{ 'size': [0.4, 0.2, 0.2], 'dir': 'right' }],
      },
    ],
  }

krokotyuk = {
    'size': [0.8, 0.8, 1.5],
    'color': '#691',
    'children': [
      { 'size': [0.1, 0.3, 0.3], 'dir': 'up', 'color': '#900' },
      { 'size': [0.4, 0.2, 0.2], 'dir': 'left' },
      { 'size': [0.4, 0.2, 0.2], 'dir': 'right' },
      {
        'size': [0.5, 0.5, 0.5],
        'dir': 'back',
        'offset': [0, 0, -0.25],
        'children': [
          {
            'size': [0.4, 0.5, 0.4],
            'dir': 'back',
            'children': [{ 'size': [0.3, 0.5, 0.3], 'dir': 'back' }],
          },
        ],
      },
    ],
  }

lady = {
    'size': [0.9, 0.9, 0.15],
    'color': '#301',
    'mass': 1,
    'children': [
      {
        'size': [0.7, 0.7, 0.15],
        'dir': 'up',
        'color': '#512',
        'children': [
          {
            'size': [0.5, 0.5, 0.15],
            'dir': 'up',
            'color': '#623',
            'children': [
            {
              'size': [0.3, 0.3, 0.5],
              'color': '#734',
              'dir': 'up',
              'children': [
              {
                'size': [0.7, 0.7, 0.1],
                'mass': 0.0001,
                'color': '#301',
                'dir': 'up',
                'children': [
                {
                  'size': [0.2, 0.2, 0.2],
                  'mass': 0.0001,
                  'dir': 'up'
                }
                ]
              }
              ] }],
          },
        ],
      },
    ],
  }
