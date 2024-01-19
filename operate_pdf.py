# 修复EOF pdf文件
def fix_pdf_EOF(file_path):
    file_name = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    fixed_file_path = os.path.join(file_dir, file_name.replace('.pdf', '') + '_fixed.pdf')

    def reset_eof_of_pdf_return_stream(pdf_stream_in: list):
        # find the line position of the EOF
        actual_line = None
        for i, x in enumerate(pdf_stream_in[::-1]):
            if b'%%EOF' in x:
                actual_line = len(pdf_stream_in) - i
                print(f'EOF found at line position {-i} = actual {actual_line}, with value {x}')
                break

        if actual_line is None:
            print('No EOF found')
            return pdf_stream_in
        else:
            # return the list up to that point
            return pdf_stream_in[:actual_line]

    with open(file_path, 'rb') as p:
        txt = (p.readlines())
    # get the new list terminating correctly
    txtx = reset_eof_of_pdf_return_stream(txt)
    # write to new pdf
    with open(fixed_file_path, 'wb') as f:
        f.writelines(txtx)

    return fixed_file_path

# 添加水印