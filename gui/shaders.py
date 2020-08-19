
vertex_shader2 = """
# version 330
in layout(location = 0) vec3 positions;
in layout(location = 1) vec3 colors;

out vec3 newColor;

void main() {
    gl_Position = vec4(positions, 1.0);
    newColor = colors;
}
"""

fragment_shader2 = """
# version 330

in vec3 newColor;
out vec4 outColor;

void main() {
    outColor = vec4(newColor, 1.0);
}
"""

vertex_shader = """# version 400
layout(location=0) in vec2 position;
layout(location=1) in vec2 texCoords;
out vec2 TexCoords;
void main()
{
    gl_Position = vec4(position.x, position.y, 0.0f, 1.0f);
    TexCoords = texCoords;
}
"""

fragment_shader = """# version 400
in vec2 TexCoords;
out vec4 color;
uniform sampler2D screenTexture;
void main()
{
    vec3 sampled = vec4(texture(screenTexture, TexCoords)).xyz; // original rendered pixel color value
    //color = vec4(TexCoords.x, TexCoords.y, 0., 1.); // to see whether I placed quad correctly
    //color = vec4(sampled, 1.0); // original
    color = vec4(sampled, 1.0); // processed (inverted)
}
"""
